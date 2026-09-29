# Representative flow

## 2026-09-29 mock 구현 후 갱신

최종 후속 결과: 사진 입력도 실제 브라우저 업로드 → mock 생성 → 미리보기 → 입주까지 PASS. 텍스트/사진 job 2개 CONSUMED를 확인한 후 진단 계정·DB 행·S3 객체 5개를 정리했다. AWS 로그인 만료는 재로그인으로 해결했다.

`IMAGE_PROVIDER=mock`과 기존 fake persona 조합을 구현했다. 실제 브라우저의 텍스트 캐릭터 생성 → Redis/Celery → FastAPI mock → 실제 S3 → 미리보기 → 입주/CONSUMED까지 통과했다. provider 기본값·RunPod adapter·FE polling은 유지했다. 상세 실행법은 `mongle-ai/docs/local-character-mock.md`, 최신 검증/남은 항목은 `local-baseline.md`의 최상단 항목을 따른다. 아래의 “미구현/미검증/AI 기동 실패”는 최초 감사 당시 이력이다.

## 추가 실측 — 2026-09-28

인증 HTTP 경로: Vite proxy → Django 정상 로그인(200) → `SourceImageCreateView.post`(201) → DB SourceImage 생성 → 응답 presigned PUT으로 S3 저장(200) → HEAD 및 GET 바이트 일치 → 진단 파일/계정 정리 PASS. 임시 계정을 만들어 정상 비밀번호 인증을 사용했다. HTTP probe 검사이며 실제 FE 업로드 함수 실행/E2E가 아니다.

`App.tsx:handleSourceImageUpload`는 FileReader 미리보기만 한다. `api.ts:uploadSourceImage`는 `generateCharacterPreview` 안에서 호출되고 바로 generation-jobs POST가 이어진다. 따라서 생성 요청 금지 조건에서는 UI 업로드만 검증할 독립 버튼이 없다. 소스 수정/요청 가로채기 없이 범위를 유지했다.

대표 추천은 사진 없는 텍스트 캐릭터 생성으로 유지한다. S3는 실제 저장소를 그대로 사용하고, mock persona/image를 붙인 뒤 기존 UI 생성·polling·입주를 검증한다. 이후 사진 입력 케이스까지 확장하면 실제 UI 업로드 E2E도 함께 확인할 수 있다.

## 후보 비교 — 소스 추적, 생성 요청 미실행

| Feature | Frontend entry | Backend endpoint | Celery task | RunPod call | Polling 여부 |
|---|---|---|---|---|---|
| TODO 분해/생성 | `mongle-web/src/features/todo/todoApi.ts:generateTodos` | `POST /api/v1/todos/generate/`, `apps/todos/views.py:TodoGenerateAIView.post` | 없음 | AI `api/todo_creation/router.py:generate` → `_run_generate` → `agents/todo_creation/todo/pipeline.py:run` → `RunPodQwenLLM.complete_raw(adapter=base)` | Django가 AI submit/poll; FE는 최종 응답 대기 |
| 플래너 대화 | `src/features/planner-chat/plannerChat.tsx`, `plannerApi.ts:chatTodos/pollTodoChatJob` | `POST /api/v1/todos/chat/`, `GET /api/v1/todos/chat/{job_id}/` | 없음 | AI `router.py:chat/_run_chat` → planner pipeline → `RunPodQwenLLM.complete_raw(adapter=planner/base)` | FE 2초/최대 600초, AI job poll, RunPod poll |
| **텍스트 캐릭터 생성 (추천)** | `src/features/character/createCharacter.tsx:handleGenerate` → `src/app/App.tsx:createCharacter` → `features/character/api.ts:generateCharacterPreview` | `POST /api/v1/characters/generation-jobs/`, `GET .../{job_id}/` | `apps.characters.tasks.process_character_generation_job` | 페르소나 `RunPodQwenLLM._complete_raw`, 이미지 `RunPodImageGenerator._submit_and_poll` | FE 2초/360초; Celery→AI 3초/300초; RunPod 2초 |
| 이미지 입력 캐릭터 생성 | 위와 같음 + `api.ts:uploadSourceImage` | 위 + `POST /api/v1/characters/source-images/` | 위와 같음 | 이미지 모드 `image_character` | 위와 같음; 선행 S3 upload/fetch 추가 |

경로에서 생략한 BE 파일은 `mongle-server/` 기준, AI 파일은 `mongle-ai/` 기준이다. RunPod 경로는 해당 provider가 `runpod`일 때의 코드 분기이며 현재 활성·성공 상태가 아니다.

## 추천 이유와 한계

**사진을 첨부하지 않는 텍스트 캐릭터 생성**을 첫 대표 기능으로 권장한다.

- FE → BE → Redis → Celery → AI 경로가 실제로 존재하고, FE가 job 상태를 polling한다.
- `source_img_id=null`이면 사진 업로드/검증/fetch를 생략한다.
- 다음 mock 단계에서 기존 `STORAGE_BACKEND=local`을 선택하면 생성 이미지는 메모리에 보관하고 data URI로 반환할 수 있다. S3 감사 로그는 best-effort이다.
- FE가 받는 preview 결과는 `gen_img_url`, `persona`로 비교적 작다. 다만 내부적으로 LLM과 이미지 provider 두 개가 필요하여 텍스트만 다루는 TODO보다 mock 계약은 크다.

네 기준 모두를 완전히 만족하는 단일 기능은 없다. 플래너는 storage와 이미지 모델이 불필요해 더 작지만 **Celery 경로가 없다**. 전체 background worker 연결 감사라는 첫 기준을 우선하여 캐릭터를 선택했다. 플래너만 mock하면 Celery 포함 E2E 검증을 했다고 말할 수 없다.

## 실제 호출 순서

```text
Frontend: mongle-web/src/features/character/createCharacter.tsx:handleGenerate
  ↓ onSubmit callback
mongle-web/src/app/App.tsx:createCharacter
  ↓
mongle-web/src/features/character/api.ts:generateCharacterPreview
  ↓ apiClient.post('/characters/generation-jobs/', payload)
Django: POST /api/v1/characters/generation-jobs/
  ↓ mongle-server/config/urls.py → apps/characters/urls.py
mongle-server/apps/characters/views.py:GenerationJobCreateView.post
  ↓ JWT 인증·serializer·활성 캐릭터 및 일일 생성 한도 확인
  ↓ CharacterGenerationJob(QUEUED), ImgGenLog 저장
  ↓ process_character_generation_job.delay(job_id, name, persona, img_gen_log_id)
Redis broker
  ↓
mongle-server/apps/characters/tasks.py:process_character_generation_job
  ↓ DB status=IN_PROGRESS
  ↓ _submit_character_job → POST {AI_SERVICE_URL}/v1/character
FastAPI: mongle-ai/api/character_creation/router.py:create_character
  ↓ CharacterJobStore.create → asyncio.create_task(_run_job)
  ↓ _run_job → api/deps.py:build_character_ports
mongle-ai/agents/character_creation/pipeline.py:run
  ↓ validate_node → llm_persona_node → sync → image_generator_node
  ↓ LLM: adapters/character_creation/qwen_llm.py:QwenLLM.generate_persona
       → adapters/character_creation/runpod_llm.py:RunPodQwenLLM._complete_raw
       → adapters/_shared/runpod_client.py:run_and_poll
  ↓ Image: adapters/character_creation/runpod_image.py:RunPodImageGenerator.generate
       → _submit_and_poll
RunPod POST /run → GET /status/{runpod_job_id}
  ↓ generated_upload_node → builder_node → CharacterEntity
AI CharacterJobStore.mark_done / mark_error
  ↓ worker _poll_character_result: GET /v1/character/{ai_job_id}
Django DB status=SUCCEEDED / FAILED
  ↓ FE api.ts:pollJob → GET /characters/generation-jobs/{django_job_id}/
Preview: gen_img_url + persona
  ↓ 명시적 입주 선택: api.ts:registerCharacter
POST /api/v1/characters/ → CharacterListView.post → Character 저장, job=CONSUMED
```

위 전체 경로는 **소스 확인**이다. 이번에 실제 실행한 Celery task는 외부 호출 없는 `cleanup_expired_refresh_tokens`이며 캐릭터 task가 아니다.

## ID와 상태

| Identifier | 생성/보관 위치 | 용도 |
|---|---|---|
| Django job UUID | `CharacterGenerationJob.job_id`, MySQL | FE가 polling/취소/입주 요청에 사용 |
| Celery task ID | Celery 메시지/result backend | broker 실행 식별자; FE job UUID와 다름 |
| AI job hex UUID | `CharacterJobStore.create`, AI process memory | worker 로컬 변수 `ai_job_id`; AI poll에 사용 |
| RunPod job ID | `/run` 응답 `id`, 각 adapter의 지역 변수 | RunPod status/cancel; FE에 전달되지 않음 |

상태: Django `QUEUED → IN_PROGRESS → SUCCEEDED → CONSUMED`; 실패/사용자 취소는 `FAILED`. AI envelope는 `pending/done/error`. RunPod는 대문자 `IN_QUEUE/IN_PROGRESS/COMPLETED/FAILED/CANCELLED/TIMED_OUT` 계열. 서로 다른 ID와 상태를 그대로 동일시하지 않는다.

## 실행 경계

확인된 것은 브라우저 초기 UI, FE proxy→BE 인증 guard, 독립 DB/Redis/worker 검사다. 인증된 생성 POST를 보내지 않았고, AI는 시작 실패 상태다. 캐릭터의 BE `AI_SERVICE_URL/TOKEN`도 빈 값이다. 따라서 실제 대표 flow의 첫 실패 HTTP 응답·DB 상태 변화는 아직 미측정이다.

“RunPod가 내려갔으니 여기까지는 될 것”이라는 추정으로 PASS를 주지 않는다. 다음 mock 단계의 검증 순서는 [runpod-boundary.md](runpod-boundary.md)의 마지막 목록을 따른다.
