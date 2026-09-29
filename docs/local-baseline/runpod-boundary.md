# RunPod boundary — 소스 확인, 호출 미실행

## 2026-09-29 mock 구현 후 갱신

최종 후속 결과: 사진 입력도 실제 브라우저 업로드 → mock 생성 → 미리보기 → 입주까지 PASS. 텍스트/사진 job 2개 CONSUMED를 확인한 후 진단 계정·DB 행·S3 객체 5개를 정리했다. AWS 로그인 만료는 재로그인으로 해결했다.

`IMAGE_PROVIDER=mock`과 기존 fake persona 조합을 구현했다. 실제 브라우저의 텍스트 캐릭터 생성 → Redis/Celery → FastAPI mock → 실제 S3 → 미리보기 → 입주/CONSUMED까지 통과했다. provider 기본값·RunPod adapter·FE polling은 유지했다. 상세 실행법은 `mongle-ai/docs/local-character-mock.md`, 최신 검증/남은 항목은 `local-baseline.md`의 최상단 항목을 따른다. 아래의 “미구현/미검증/AI 기동 실패”는 최초 감사 당시 이력이다.

## 현재 기준의 최소 mock 제안 — 2026-09-28 (미구현)

- **삽입 위치:** `mongle-ai/api/deps.py`의 character Ports 조립에서 LLMPort/ImageGeneratorPort 구현을 선택한다. 페르소나의 기존 fake 구현 재사용 가능성을 먼저 검토하고, image에는 유효한 PNG bytes를 반환하는 작은 provider를 추가한다.
- **유지할 interface:** `LLMPort.generate_persona → LLMPersonaResult`, `ImageGeneratorPort.generate → ImageGenerationResult`; AI pending/done/error envelope, Django job UUID/status, FE polling 계약. 기존 RunPod HTTP adapter 자체는 변경하지 않는다. HTTP 수준 mock을 선택할 경우 아래 `/run`, `/status/{id}`, cancel 계약을 지켜야 한다.
- **파일 후보:** AI `api/config.py`, `api/deps.py`, character mock image adapter, 필요한 계약 검사와 `.env.example`/실행 문서. BE는 우선 소스 변경 없이 `AI_SERVICE_URL`, `AI_SERVICE_TOKEN`을 AI의 주소 및 `MONGLE_API_KEY`와 맞춘다.
- **변경하지 않을 영역:** FE 업로드/polling, Django 모델·task·router, Redis/Celery, AI job store, 운영 RunPod adapter, 패키지 버전, S3 구현. S3 연결이 완료됐으므로 현재 `STORAGE_BACKEND=s3` 유지가 가능하다. 아래 최초 제안의 local storage는 오프라인 대안이며 필수 전환이 아니다.
- **mock 후 검증 flow:** FastAPI 기동/내부 인증 → 실제 UI 텍스트 생성 → Django QUEUED → Celery IN_PROGRESS → AI pending → mock persona/image → 실제 S3 → done → Django SUCCEEDED → FE preview → 입주/CONSUMED. 이후 사진 첨부 업로드 E2E와 실패/환불/취소를 검증한다. RunPod outbound가 없고 허용한 S3만 호출되는지 확인한다.

아래 경계·payload·timeout 분석은 그대로 유효하다. 대표 생성은 아직 실행하지 않았으며 이 제안은 구현 권한을 대신하지 않는다.

대표 기능: **사진 없는 텍스트 캐릭터 생성**. 상세 FE → BE → worker 경로는 [representative-flow.md](representative-flow.md). 현 상태에서는 FastAPI가 설정 검사에서 종료하므로 아래는 네트워크 실측 결과가 아니라 실제 코드의 계약이다.

## 실제 client와 교체 경계

| Boundary | File / function | 역할 |
|---|---|---|
| Provider 조립 | `mongle-ai/api/deps.py:build_character_ports`, `_build_character_llm`, `_get_image_generator` | pipeline의 LLMPort/ImageGeneratorPort 구현 선택 |
| Persona adapter | `mongle-ai/adapters/character_creation/runpod_llm.py:RunPodQwenLLM._complete_raw` | persona messages → RunPod payload → `output.text` |
| LLM submit/status transport | `mongle-ai/adapters/_shared/runpod_client.py:run_and_poll` | 동일 함수 안에서 POST `/run`, GET `/status/{id}` |
| Image adapter/transport | `mongle-ai/adapters/character_creation/runpod_image.py:RunPodImageGenerator.generate`, `_submit_and_poll`, `_cancel_job` | image payload, 별도의 submit/status loop, base64 decode, cancel |
| Domain interfaces | `mongle-ai/agents/character_creation/protocols.py:LLMPort`, `ImageGeneratorPort` | provider와 application pipeline의 명확한 경계 |
| Configuration | `mongle-ai/api/config.py:AppConfig.from_env` | provider별 필수 env 검증; 현재 startup 실패 지점 |

**LLM 공용 `run_and_poll` 하나만 바꾸면 이미지 호출은 여전히 RunPod로 나간다.** 반대로 BE `infrastructure/image_gen/client.py`의 `/runsync`를 바꿔도 현재 캐릭터 경로에는 영향이 없다. 이 둘을 혼동하지 않는다.

## 제출·조회와 payload

### BE → AI (GPU provider 경계보다 앞)

`mongle-server/apps/characters/tasks.py:_submit_character_job`:

```text
POST {AI_SERVICE_URL}/v1/character
X-API-Key: <AI_SERVICE_TOKEN — 값 비공개>
```

```json
{
  "user_id": "<user UUID>",
  "name": "<name>",
  "persona": "<user text>",
  "personality_keywords": [],
  "source_image_key": "",
  "source_image_content_type": "",
  "source_image_url": ""
}
```

FastAPI `create_character`는 `CharacterJobStore.create()`의 ID를 `202 {status:"pending", result:{job_id:"..."}, error:null}` envelope로 반환한다. worker는 `_poll_character_result`로 `GET /v1/character/{ai_job_id}`를 반복한다.

- pending: `result:null`.
- done: `result:CharacterEntity`.
- error: `error:{code:"character_generation_failed",message:"..."}`.
- 없는 ID: HTTP 404.

`CharacterEntity` 필드: `character_id`, `user_id`, `name`, `persona`, `personality`, `speech_style`, `background`, `appearance`, `appearance_payload`(nullable), `image_url`, `source_image_url`(nullable), `created_at`, `timings`.

worker는 image URL, appearance, appearance_payload, 합성 persona를 DB job에 저장한다. `gen_img_object_key`는 `result.get(..., "")`로 읽지만 현 AI `CharacterEntity`에는 해당 필드가 없다. 나중에 Django 등록 view가 URL로부터 fallback 추출한다. 이 차이도 임의로 수정하지 않았다.

### Persona RunPod LLM

`QwenLLM.generate_persona`가 system/user messages를 구성하고 `_complete_raw`에 넘긴다. RunPod adapter는 다음을 전송한다.

```text
POST {RUNPOD_CHARACTER_ENDPOINT_URL}/run
Authorization: Bearer <RUNPOD_API_KEY — 값 비공개>
```

```json
{
  "input": {
    "adapter": "character",
    "messages": [{"role":"system","content":"<prompt>"},{"role":"user","content":"<input>"}],
    "temperature": 0.1,
    "max_tokens": 600
  }
}
```

submit 응답에서 `id`를 필수로 읽고, `GET {endpoint}/status/{id}`를 반복한다. 완료 응답 계약:

```json
{
  "id": "<runpod job id>",
  "status": "COMPLETED",
  "output": {"text": "<JSON 문자열>"}
}
```

`output.text`는 **JSON object 자체가 아닌 문자열**이다. `_parse`가 이 문자열을 `LLMPersonaResult`로 검증한다. 필수 필드: `personality`, `speech_style`, `background`, `appearance`, `appearance_en`(비어 있으면 안 됨). 후속 image prompt는 `appearance_en → appearance → fallback_persona` 순서를 따른다.

### Image RunPod

`RunPodImageGenerator.generate` → `_submit_and_poll`:

```text
POST {RUNPOD_IMAGE_ENDPOINT_URL}/run
Authorization: Bearer <RUNPOD_API_KEY — 값 비공개>
```

사진 없는 대표 flow의 입력:

```json
{
  "input": {
    "mode": "text_character",
    "seed": 123,
    "persona": "<appearance prompt>",
    "prompt": "<appearance prompt>",
    "prompt_en": "<English appearance tags>"
  }
}
```

위 seed는 형태 설명용 예시다. 실제 코드는 매 호출 `random.randint(0, 2**32-1)`을 사용한다. `prompt_en`은 값이 있을 때만 넣는다. 이미지 입력은 mode=`image_character`, `image`와 `source_image_b64`를 넣는다. feed는 mode=`feed`, `appearance`, `quest_ko`, `prompt`를 넣는다.

`GET {endpoint}/status/{id}` 완료 응답의 `output.image` 또는 `output.image_b64`에서 base64를 읽어 bytes로 변환한다. `output.appearance`는 선택적 구조화 metadata다.

```json
{
  "id": "<runpod image job id>",
  "status": "COMPLETED",
  "output": {"image_b64":"<base64 PNG>","appearance":{}}
}
```

반환 타입은 `ImageGenerationResult(image_bytes: bytes, appearance_payload: dict | None)`. 이미지 bytes는 다음 `generated_upload_node`가 storage에 저장한다. PNG bytes를 이미지 URL 문자열로 대체하면 domain interface를 깨뜨린다.

## Status mapping / retry / timeout / errors

| 계층 | Submit / poll | Timeout | Retry 및 오류 처리 |
|---|---|---|---|
| FE character | POST job, GET job | poll 2초, 전체 360초 | SUCCEEDED preview; FAILED 친화적 오류; TIMEOUT이면 재개용 pending 상태 유지; CANCELLED 시 중단 |
| Celery → AI | `_submit_character_job`, `_poll_character_result` | request 30초, poll 3초, 전체 300초 | done 결과 반환; error/HTTP/timeout은 task catch; DB FAILED 및 일일 횟수 환불 |
| AI async job | `_run_job`, `get_character_job` | route 자체에 전체 timeout 없음 | catch Exception → job ERROR/code/message; HTTP polling으로 전달 |
| LLM transport | `run_and_poll` | request 30초, poll 2초, 기본 총 300초 | submit 자동 retry 없음; 연속 HTTP poll 오류 3회 시 RunPodJobError; 성공 poll 뒤 counter reset |
| Persona adapter | `_complete_raw` / `generate_persona` | transport 값 사용 | RunPodJobError → LLMFailedError; text 누락도 LLMFailedError; persona JSON/schema 재시도 최대 3회 |
| Persona graph | `pipeline.py:build_graph` | 별도 전체 timeout 없음 | LLMFailedError에 node 최대 3 attempts; parse 재시도와 겹칠 수 있음 |
| Image transport | `_submit_and_poll` | request 30초, poll 2초, 총 600초 | 연속 poll HTTP error 3회 또는 timeout 때 `/cancel/{id}` best-effort; generate가 ImageGenerationFailedError로 변환 |
| Image graph | `nodes/image_generator.py` | adapter 값 사용 | ImageGenerationFailedError에 최대 2 attempts; 실패 시 cleanup 분기 |
| Storage | source_upload / generated_upload | 구현별 HTTP/SDK 정책 | source graph 최대 4 attempts, generated node 최대 4 attempts; 실패 cleanup |

RunPod `COMPLETED`는 output 해석으로 진행한다. `FAILED/CANCELLED/TIMED_OUT`는 terminal error다. `IN_QUEUE/IN_PROGRESS`를 포함한 그 밖의 상태는 계속 기다린다. Image client는 RunPod 상태가 COMPLETED여도 `output.status == "failed"`이면 실패로 처리한다.

LLM helper는 malformed JSON/submit `id` 누락을 HTTPError로 감싸지 않는다. 이후 AI job의 broad catch까지 올라갈 수 있다. timeout 검사는 각 계층 poll 반복 안에 있으므로 엄격한 end-to-end 벽시계 제한은 아니다. LLM poll HTTP 오류 분기는 timeout 검사보다 재시도 횟수 제한을 먼저 따른다.

**Celery의 `max_retries=3` 선언만 보고 자동 retry가 있다고 판정하지 않는다.** `process_character_generation_job`은 `self.retry`/autoretry 없이 예외를 잡고 FAILED 처리 후 반환한다. 따라서 Celery execution SUCCESS와 application job SUCCEEDED는 다른 개념이다. `CharacterJobStore` 주석의 “실패 후 재시도” 역시 task 코드상 자동 보장은 없다.

외부 image 600초·LLM 300초에 비해 Celery→AI 전체 poll 300초, FE poll 360초라는 예산 차이가 있다. 실제 지연 문제를 측정한 것은 아니며 이번에는 변경하지 않는다.

별도 `api/character_creation/router.py:warmup_character` → `adapters/_shared/runpod_warmup.py:warm_character_endpoints`도 RunPod `/health`와 조건부 `/run`을 호출한다. 이번에는 실행하지 않았다. 다음 mock 모드에서는 endpoint를 비워 해당 경로가 외부에 나가지 않도록 함께 검증해야 한다.

## 다음 단계 제안 — 아직 구현하지 않음

- **mock provider를 넣을 위치:** `api/deps.py`의 character `Ports` 조립 지점에서 명시적 mock mode를 선택한다. `LLMPort.generate_persona` 및 `ImageGeneratorPort.generate`를 충족하는 구현을 주입하고 기존 async job·polling·Django worker 경로는 통과시킨다. 기존 `adapters/character_creation/fake_llm.py` 재사용 가능성을 먼저 확인한다. 이미지 mock은 PNG bytes + appearance metadata를 반환하는 작은 구현이면 된다. RunPod HTTP transport 자체 검증은 별도 계약 테스트로 다룬다.
- **유지해야 할 interface:** `generate_persona(*, name, persona, keywords) -> LLMPersonaResult`; `generate(*, user_id, llm_result, fallback_persona, source_image_bytes) -> ImageGenerationResult`; 위 persona/image 필드와 domain exception 계약. HTTP job을 모사하는 방식으로 확장할 경우 `/run → {id}`와 `/status/{id} → {status,output,error}` 및 image cancel 계약까지 유지한다. FE/BE의 job ID와 envelope를 바꾸지 않는다.
- **변경이 필요한 파일 후보:** `mongle-ai/api/config.py` (mock 분기에서는 미사용 GPU credential/LoRA 검증을 요구하지 않도록 명시적 처리), `api/deps.py` (구현 선택), `adapters/character_creation/`의 작은 mock image 모듈과 필요 시 persona fixture, 관련 config/adapter/API 계약 tests, `.env.example` 또는 로컬 실행 문서. BE는 우선 코드 변경 없이 `AI_SERVICE_URL=http://127.0.0.1:8010`, `AI_SERVICE_TOKEN=MONGLE_API_KEY와 동일한 로컬 값`으로 연결한다. 실제 secret 값은 문서에 넣지 않는다.
- **변경하지 않아야 할 영역:** FE polling·타이머·UI, Django views/tasks/models/migrations, Redis/Celery topology, AI job stores/envelope, 운영 RunPod adapter/worker 배포 파일, provider 밖 LangGraph 로직, 패키지 버전. S3는 새 구현 대신 기존 `STORAGE_BACKEND=local`로 선택한다. 첫 범위는 사진 없는 생성·preview·입주까지다.
- **mock 도입 후 검증할 flow:** AI lifespan/health 및 내부 키 인증 → 로컬 인증 사용자 → FE 생성 POST/202 → Django job QUEUED → Redis/Celery 수신 → IN_PROGRESS → AI pending → mock persona/image → 기존 local storage → done → Django SUCCEEDED → FE preview 표시 → 입주 POST/201 → DB Character와 CONSUMED. 추가로 실패/timeout/취소의 FAILED·환불·중복 입주 거부를 검증한다. RunPod/S3 outbound request가 없는지, `data:` 이미지가 FE에서 표시되고 등록 후에도 유지되는지 확인한다. 이 검증을 마치기 전에는 대표 flow PASS를 선언하지 않는다.
