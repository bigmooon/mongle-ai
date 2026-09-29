# Local baseline — 2026-09-26

## 2026-09-29 RunPod mock 도입 후 상태

현재 검증 범위: FE/BE/DB/Redis/Celery/FastAPI와 실제 S3를 사용한 캐릭터 텍스트·사진 입력 생성/입주 PASS. 실제 RunPod는 호출 미실행이다. 최초 STEP 1–9 진단은 완료됐으며, mock 성공은 기존 RunPod adapter/HTTP transport 성공을 의미하지 않는다.

최초 진단의 코드 변경 금지는 사용자의 다음 작업 지시로 이번 mock 도입 범위에서 해제되었다. AI provider 경계만 변경했으며 FE·Django·Celery·polling·패키지 manifest/lock은 변경하지 않았다.

- `IMAGE_PROVIDER=mock` 추가, 기존 `LLM_PROVIDER=fake` 재사용. mock은 64×64 진단 PNG이며 실제 AI 이미지가 아니다.
- FastAPI 8010 기동 및 health 성공. 기존 S3 유지, 로컬 내부 공유 키를 AI/BE의 gitignored `.env`에 맞춰 저장. Django/worker 재시작 완료.
- **실제 브라우저 텍스트 생성 PASS:** 정상 로그인 → FE 생성 버튼 → Django job → 실제 Redis/Celery → FastAPI job → fake persona/mock image → 실제 S3 → Django SUCCEEDED → 기존 FE polling/미리보기 → 입주 → DB Character 1건 및 job CONSUMED 확인.
- 브라우저가 받은 미리보기 이미지의 naturalWidth/naturalHeight 64×64, complete=true 확인.
- 선택 검사: AI 152 passed, Django characters 53 passed. 신규 검사에서 소켓 연결을 차단한 채 실제 lifespan/config/provider/job 계약과 PNG CRC를 검증했다. 전체 저장소 coverage gate나 GPU 품질을 검증한 것은 아니다.
- 기존 LangChain/Starlette deprecation 및 Django test JWT key 길이 경고는 기록하고 변경하지 않았다.
- 2026-09-29 재개 시 FE가 종료되어 재시작했다. Django/AI는 실행 중이었다. AWS SDK는 CredentialRetrievalError를 반환했고 AWS 재로그인이 필요한 상태다.
- **AWS 재로그인 후 사진 입력 브라우저 E2E PASS:** 기존 파일 선택 UI로 진단 PNG 입력 → 생성 버튼 → 브라우저 S3 PUT → SourceImage UPLOAD_COMPLETED → AI 원본 fetch → mock 생성 → S3 결과 → 기존 polling → 미리보기 → 입주 CONSUMED. 원본 S3 바이트가 업로드 파일과 정확히 일치함을 확인했다.
- 텍스트/사진 job 총 2개 CONSUMED, Character 2건을 확인했고 양쪽 생성 이미지 GET 성공. 사진 미리보기는 실제 스크린샷으로 확인했다(추가 DOM 이미지 속성 조회는 도구 timeout이 있어 성공 증거로 사용하지 않음).
- **정리 완료:** 브라우저 정상 로그아웃 후 worker active/reserved 비어 있음 확인. 진단 계정 UUID에 한정해 S3 생성 이미지 2개·원본 1개·감사 로그 2개(총 5개)를 삭제하고 해당 prefix가 비었음을 재조회했다. 진단 사용자와 관련 DB 행도 삭제하고 부재 확인. 사용자 데이터와 다른 버킷 객체는 변경하지 않았다.
- 이번 단계 판정: **mock 기반 캐릭터 생성 E2E 완료.** 실제 RunPod, TODO/플래너/피드 전체, 실서비스 장애/timeout E2E는 이 성공 판정에 포함하지 않는다.

실행 방법과 mock 한계는 `mongle-ai/docs/local-character-mock.md` 참조. TODO/플래너/피드 전체 mock은 이번 범위가 아니다. 과거 실패 기록은 당시 상태이며 이 절의 성공 결과와 구분한다.

## 이전 감사 판정 — 2026-09-28T01:27:26+09:00

초기 요청 STEP 1–9의 상세 증거는 아래 이력 및 나머지 네 문서에 정리했다. 이 절은 2026-09-28 당시 기록이다. 현재 판정은 위의 2026-09-29 mock 도입 후 상태를 우선한다.

| 계층 | 현재 판정 | 실제 확인 범위 |
|---|---|---|
| Frontend | PASS | 브라우저 초기 화면, HTTP 200; 기존 build/typecheck PASS |
| Backend | PASS | health 200, Vite proxy 경유 실제 로그인 200, 인증된 업로드 API 201 |
| Database | PASS | migration 미적용 0, 진단 계정·SourceImage 쓰기/조회/삭제 |
| Redis | PASS | 실제 cache set/get/delete |
| Celery | PASS | 현재 worker pong; 실제 단순 task 수신/SUCCESS는 최초 감사 기록 |
| S3 | PASS | 실행 중 Django가 발급한 서명으로 PUT 200, HEAD 크기, GET 바이트 일치, 정리 성공; 앞선 AI adapter/CORS 검사도 PASS |
| AI API | FAIL | 현재 AppConfig.from_env가 MONGLE_API_KEY, QWEN_BASE_URL, QWEN_MODEL, LORA_DIR 누락으로 실패 |
| RunPod | Unavailable / 호출 미실행 | 사용자 제공 인프라 중단 상태; 원격 장애를 새로 측정하지 않음 |
| Representative AI flow | NOT RUN | 생성 요청 금지 범위 유지. RunPod 호출 직전까지 PASS라고 판정할 근거 없음 |
| 브라우저 업로드 E2E | NOT RUN | 기존 UI가 S3 업로드 직후 AI job을 제출하므로 이번 제한과 분리 실행 불가 |

> 현재 로컬에서 웹 초기 화면과 기본 서비스, 실제 인증 HTTP API → DB → S3 저장·조회까지 정상 동작한다. AI API는 필수 설정 및 모델/provider 준비 부족으로 시작하지 못하며, 외부 RunPod 호출 경계까지의 실행은 아직 검증하지 않았다.

### 이번 추가 검증과 정리

- 별도 임시 계정을 로컬 진단 MySQL에 일반 사용자로 생성하고, 토큰을 직접 만들거나 인증을 우회하지 않고 정상 `/api/v1/auth/login`으로 로그인했다. 회원가입/이메일 인증 흐름을 검증한 것은 아니다.
- `http://127.0.0.1:5173/api/v1/characters/source-images/`를 HTTP로 호출하여 Vite proxy → 실행 중 Django → MySQL → 실제 S3 경로를 확인했다. **브라우저 클릭으로 실행한 결과는 아니다.**
- 응답의 presigned PUT으로 1픽셀 PNG를 업로드하고 HEAD/GET 바이트를 확인했다. 생성한 S3 객체와 임시 사용자/관련 DB 행만 삭제했다. 비밀번호·JWT·서명 URL은 출력/문서화하지 않았다.
- 최초 진단용 비밀번호가 API의 최대 16자 제한을 넘어서 로그인 400을 받았다. 기존 `apps/users/validators.py:validate_password` 규칙에 맞게 일회성 진단 입력만 수정한 후 성공했다. 애플리케이션 결함으로 처리하지 않았다.
- AI generation job 수는 검사 전후 동일하다. RunPod/AI 생성·warmup 요청 없음. 소스·패키지·polling·설정 파일 변경 없음. 기존 실행 프로세스를 재사용했으며 업로드 API 성공으로 S3 설정 반영도 확인했다.

### 다음 단계 시작 가능 여부

**READY — RunPod mock provider 도입 단계에 착수할 수 있다. 구현은 아직 하지 않았다.**

S3는 이제 실제 provider를 유지할 수 있다. `runpod-boundary.md`의 최소 범위에 따라 character persona/image provider를 선택 가능하게 하고 AI 내부 인증/주소 설정을 연결하는 것이 다음 작업이다. 실제 UI 업로드와 AI 생성/polling/입주 검증은 mock 도입 이후 한 흐름으로 수행한다.

## 2026-09-28 프런트엔드 이미지 업로드 후속 검증

검사 시각: 2026-09-28 01:06 KST. 아래 S3 연결 성공 기록을 기준으로 서비스를 다시 점검했다.

**결론: 로컬 서비스와 AWS 세션은 정상. 실제 프런트엔드 업로드는 로그인 경계에서 BLOCKED이며, S3 업로드 성공으로 판정하지 않는다.**

| 항목 | 관측 결과 | 판정 |
|---|---|---|
| AWS 로그인 | `mongle-login`, `mongle-dev` 각각 STS 인증 성공. 재로그인 불필요 | PASS |
| S3 설정 | Django 설정을 로드한 별도 진단 프로세스에서 기존 `get_s3_client().head_bucket()` 성공 | PASS (읽기 전용 접근) |
| DB | 기존 `mongle-baseline-mysql` 실행 중, 미적용 migration 0 | PASS |
| Redis | 기존 `mongle-baseline-redis` 실행 중, Django cache set/get/delete 성공 | PASS |
| Django | 시작 시 8000 미기동 → 기존 `.env`를 읽어 새로 시작. `/health/` HTTP 200 | PASS |
| Celery | 시작 시 ping 응답 없음 → `baseline@localhost` worker 시작. pong, active/reserved/scheduled 각각 0 | PASS (연결·제어; 이번에는 task 미제출) |
| Frontend | 시작 시 5173 미기동 → 기존 Vite 시작. 페이지 HTTP 200, 실제 브라우저 초기 UI 표시, 수집된 console warn/error 0 | PASS |
| FE → Django proxy | `/api/v1/todos/` HTTP 401 | PASS (미인증 guard) |
| 실제 화면 진입 | 튜토리얼 닫기 → ‘이장님과 대화’ 클릭 → ‘로그인이 필요해요.’ 및 로그인 모달 | BLOCKED (인증) |
| 업로드 API 인증 | 별도 HTTP probe로 proxy 경유 `POST /api/v1/characters/source-images/`에 빈 JSON 전송 → 401 | PASS (미인증 guard만) |
| 브라우저 파일 선택·미리보기 | 로그인된 계정이 없어 해당 화면에 진입하지 못함 | NOT RUN |
| 브라우저 → S3 PUT | 서명 발급 및 업로드 미실행 | NOT RUN |
| AI/RunPod/생성 | AI 8010 미기동 유지, 생성 API 호출 및 job 제출 없음 | NOT RUN (요청 범위 밖) |

### 확인된 실패·중단 경계

1. **현재 실제 차단점은 로그인이다.** 진단 DB의 사용자 수는 0이었다. 새 계정·seed·인증 토큰을 만들거나 인증을 우회하지 않았다. 브라우저 초기 token refresh의 401은 세션이 없는 상태와 일치한다.
2. **파일 선택과 S3 업로드는 다른 단계다.** `mongle-web/src/app/App.tsx:805`의 `handleSourceImageUpload()`는 `FileReader.readAsDataURL()`로 로컬 미리보기만 만든다. `mongle-web/src/features/character/api.ts:133`의 `uploadSourceImage()`가 서명 발급 → S3 PUT을 수행하지만 독립 export/UI가 없다. 같은 파일의 `generateCharacterPreview()`는 업로드 직후 `/characters/generation-jobs/`를 제출한다. 따라서 현재 UI에서 생성 동작을 누르는 검사는 ‘AI 생성 요청 금지’ 범위를 넘는다. 이는 코드로 확인한 경계이며 S3 실패를 관측한 것은 아니다.
3. 후속 검증에는 로컬 로그인 계정과 **생성 요청 없이 업로드만 실행할 수 있는 검증 방식**이 필요하다. 이번에는 생성 버튼 클릭, 네트워크 응답 대체, mock, polling 변경을 하지 않았다.

종료 시 DB의 사용자·SourceImage·CharacterGenerationJob은 각각 0건이었다. 이번 Django 로그의 generation-jobs 요청은 0건이며 Celery active/reserved/scheduled도 각각 0건이다. S3 객체를 새로 만들지 않았고, 앞선 S3 저장·조회·삭제 PASS를 이번 브라우저 E2E 성공으로 합산하지 않았다.

DB·Redis는 기존 컨테이너를 유지했고 Django(127.0.0.1:8000)·Celery·Frontend(127.0.0.1:5173)는 실행 상태로 남겼다. 새 프로세스는 기존 `.env`를 읽는다. 소스·패키지·lock·polling·`.env` 변경 없음; 세 저장소의 `git status --short`는 시작·종료 모두 clean. 인증정보·계정 식별값·서명 URL은 출력하거나 문서에 저장하지 않았다.

최초 제한된 실행에서 Docker 소켓 접근과 AWS endpoint 연결이 차단되었지만, 승인된 로컬/네트워크 실행에서 Docker 조회 및 두 프로필의 STS 검사가 성공했다. 이를 서비스 장애나 세션 만료로 분류하지 않는다. 일회성 진단의 S3 client 함수명 오기(`_get_client`)는 기존 실제 함수 `get_s3_client`로 바로잡아 재실행했으며 소스 변경은 없었다.

## 2026-09-28 S3 연결 후속 검증

아래 최초 감사 결과는 2026-09-26 당시 기록이다. **S3는 후속 검증에서 PASS로 갱신되었다.** 다른 서비스와 대표 AI flow는 이번 작업에서 재검증하지 않았다.

- 버킷: `mongle-dev-asset`, 리전: `ap-northeast-2`, 퍼블릭 액세스 차단 4개 모두 활성화.
- CORS: `http://localhost:5173`, `http://127.0.0.1:5173`; GET/PUT/HEAD 허용. 두 origin의 실제 PUT preflight HTTP 200 확인.
- Django 기존 `infrastructure/storage/s3.py`: presigned PUT → HEAD 크기 확인 → presigned GET 바이트 일치 → 삭제 PASS.
- AI 기존 `api/deps.py:_s3_client`, `adapters/character_creation/s3_storage.py:S3Storage`: 업로드 → presigned GET 바이트 일치 → 삭제 PASS. 전체 FastAPI 앱을 시작한 검사는 아니다.
- 각 검사에서 `mongle-village/diagnostics/<uuid>.png`에 임시 PNG 하나를 업로드했으며 모두 삭제했다.
- 로컬 `mongle-login` 로그인 세션을 사용하는 `mongle-dev` credential_process 프로필 설정. 양쪽 저장소의 gitignored `.env` 생성; 인증정보 값 저장 없음.
- 소스·패키지·RunPod·polling 변경 없음. DB/AI 업무 요청 없음. 기존 실행 프로세스는 재시작하지 않았으므로 새 환경변수 반영에는 재시작이 필요하다.

현재 결론: **실제 S3 저장·조회 경계는 정상이다. RunPod 연결 및 대표 AI 생성 E2E는 여전히 미검증이다.**

## 최초 감사 판정

> 현재 로컬 환경에서 프런트엔드 페이지·API proxy, Django, MySQL 읽기/쓰기, Redis 및 Celery의 실제 task 처리까지 각각 정상 동작한다. AI 서비스는 필수 환경변수 누락으로 시작되지 않으며, 그 이후의 RunPod·S3 연동은 확인하지 못했다. **대표 AI flow가 RunPod 호출 직전까지 정상이라는 결론은 아직 낼 수 없다.**

```text
Frontend: PASS — 초기 페이지, console, typecheck, build, API proxy
Backend: PASS — Django system check, HTTP health, 인증 guard
Database: PASS — MySQL 9.7.0, migration 전부 적용, 읽기/쓰기/rollback
Redis: PASS — 실제 캐시 set/get/delete, Celery broker/result backend
Celery: PASS — broker 연결, 7개 task 등록, 실제 task SUCCESS
AI API (FastAPI): FAIL — MissingEnvError, port 8010 미기동
Representative flow: NOT RUN — 요청의 STEP 6에 따라 생성 요청 미실행
RunPod: Unavailable — 사용자 제공 상태, 키 미설정; 원격 상태 재검증하지 않음
S3: Unavailable in this configuration — 버킷 미설정; 원격 장애 판정 아님
```

PASS는 위에 명시한 검사 범위에만 해당한다. 로그인·회원가입·인증된 업무 API·AI 생성 E2E를 통과했다는 뜻이 아니다. DB/worker의 독립 검사를 하나의 연속된 대표 flow 성공으로 합산하지 않았다.

## 감사 대상과 변경 범위

작업 위치: `/Users/jpaper/Documents/projects/mong-studio`. 상위 폴더 자체는 Git 저장소가 아니고 아래 세 개가 독립 저장소다.

| Repository | 검사한 HEAD | 시작 시 상태 |
|---|---|---|
| mongle-web | `27ae3b4` | clean |
| mongle-server | `0f00160` | clean |
| mongle-ai | `edb3c42` | clean |

macOS arm64, Node 24.12.0, npm, uv 0.9.18, Python 3.12.12, Docker Engine 29.4.0을 사용했다. 기존 다른 프로젝트의 PostgreSQL/컨테이너는 변경하지 않았다.

애플리케이션 소스·환경변수 예제·의존성 manifest·lock·migration은 변경하지 않았다. `.env`를 만들지 않았으며 seed 계정도 생성하지 않았다. 추가된 것은 이 폴더의 감사 문서 5개, 각 Python `.venv`, FE `node_modules`/`dist`, 진단 컨테이너·DB, 임시 패키지 캐시다. 외부 secret을 읽거나 출력하지 않았다. RunPod 배포·AI job 제출·S3 업로드·mock 구현·polling 수정은 하지 않았다.

## 실행 증거

아래 명령은 각 repository 디렉터리에서 실행했다. DB URL은 운영 접속 정보가 아니라 이번에 생성한 **loopback 전용·비밀번호 없는 폐기 가능한 DB** 주소다.

| Service | Command / probe | Expected | Actual | Result |
|---|---|---|---|---|
| DB | `docker run ... mysql:9.7` | DB 기동 | `SELECT VERSION()` → `9.7.0` | PASS |
| DB schema | `DATABASE_URL=mysql://root@127.0.0.1:3306/mongle .venv/bin/python manage.py migrate --noinput` | 전체 적용 | 모든 migration `OK`; MigrationExecutor 미적용 0 | PASS |
| DB schema | 동일 env로 `manage.py makemigrations --check --dry-run` | 모델과 migration 일치 | `No changes detected` | PASS |
| DB I/O | `IntervalSchedule` 행 생성·조회 후 transaction rollback | 쓰기/읽기 및 원복 | write/read=True, rollback=True | PASS |
| Redis | Django `cache.set/get/delete` | 값 반환 후 삭제 | `ok` | PASS |
| Backend | `manage.py check` | 설정 정상 | `System check identified no issues (0 silenced).` | PASS |
| Backend | `manage.py runserver 127.0.0.1:8000 --noreload` + `GET /health/` | 200 | `200 {"status":"ok"}` | PASS |
| Backend auth | `GET /api/v1/todos/` without JWT | 401 | `Authentication credentials were not provided.` | PASS (인증 guard만) |
| Celery | `celery -A config worker --pool=solo --concurrency=1 --hostname=baseline@localhost --loglevel=info` | ready, 등록 성공 | Redis connected, 7개 task, `ready` | PASS |
| Celery control | `app.control.ping(timeout=3)` | pong | `baseline@localhost: {ok: pong}` | PASS |
| Celery task | `cleanup_expired_refresh_tokens.delay()` → `.get(timeout=15)` | broker 수신/실행/result 저장 | result=None, state=`SUCCESS` | PASS |
| Frontend | `npm ci --ignore-scripts --no-audit --no-fund` | lock 기반 설치 | 344 packages installed | PASS (재시도 후) |
| Frontend | `npm run build` | typecheck 및 build | 913 modules; exit 0 | PASS |
| Frontend | `npm run dev -- --strictPort` | 5173 기동 | Vite 5.4.21 ready | PASS |
| Frontend HTTP | `GET http://127.0.0.1:5173/` | HTML 200 | 200 | PASS |
| Browser | 초기 페이지 DOM 및 console | 화면 렌더링, 치명적 오류 없음 | 몽글마을·로그인·튜토리얼·TODO UI 표시; error/warn 0 | PASS (초기 화면만) |
| FE → BE | `GET http://127.0.0.1:5173/api/v1/todos/` | proxy → BE 인증 guard | 직접 BE 호출과 같은 401 JSON | PASS |
| AI API | `.venv/bin/uvicorn api.main:app --host 127.0.0.1 --port 8010` | FastAPI 기동 | `MissingEnvError`; exit 3 | FAIL |
| AI health | `GET http://127.0.0.1:8010/health` | 200 | `[Errno 61] Connection refused` | FAIL |
| S3 config | `_ensure_storage_configured()` | 버킷 설정 존재 | `StorageNotConfiguredError: AWS_S3_BUCKET is not configured` | FAIL (설정) |

Celery 검사는 진단 DB의 refresh token 수가 0임을 먼저 확인한 뒤 기존 정리 task를 1회 실행했다. 사용자 토큰은 없었고 외부 AI 호출은 없다. 결과 backend의 해당 task 결과도 `.forget()`으로 지웠다. DB I/O 검사용 행은 rollback했다. Celery Beat는 기동하지 않았다.

### 정확한 시작 실패와 경고

1. 최초 sandbox 내 `uv sync`는 macOS system-configuration에서 `Attempted to create a NULL object.` / `Tokio executor failed`로 exit 101. 캐시 접근에도 `Operation not permitted`가 있었다. 실행 권한 경계를 조정하고 `/tmp` 캐시로 재실행하여 동일 lock 설치 성공. 프로젝트 코드 문제로 분류하지 않는다.
2. 최초 Docker 소켓 접근은 `permission denied ... docker.sock`. 승인된 실행으로 Docker 사용 가능 확인 및 진단 컨테이너 생성 성공.
3. 최초 sandbox 내 npm 설치는 `npm error Exit handler never called!`로 실패. 같은 lock/명령을 승인된 실행으로 재시도해 성공. 패키지 변경 없음.
4. AI 기본 설정의 실제 실패:

   ```text
   api.config.MissingEnvError: 다음 환경변수가 필요합니다: MONGLE_API_KEY, QWEN_BASE_URL, QWEN_MODEL, LORA_DIR
   ERROR: Application startup failed. Exiting.
   ```

5. `.env.example`를 **별도 일회성 설정 검사 프로세스에서만** 읽어도 다음과 같이 실패한다. 파일 복사·fake 모델 실행은 하지 않았다.

   ```text
   LLM_PROVIDER=fake, QUEST_LLM_PROVIDER=fake, FEED_LLM_PROVIDER=fake
   IMAGE_PROVIDER=runpod, STORAGE_BACKEND=s3
   MissingEnvError: 다음 환경변수가 필요합니다: RUNPOD_API_KEY, AWS_S3_BUCKET, AWS_REGION
   ```

6. FE build의 500 kB 초과 chunk 경고와 AI import의 LangChainPendingDeprecationWarning은 존재한다. 빌드 실패 원인이 아니며 최적화나 버전 변경을 하지 않았다.

## 재현·실행 상태

정확한 설치·실행·종료 명령은 [runtime-dependencies.md](runtime-dependencies.md)에 있다. 감사 종료 시 FE 5173, Django 8000, Celery worker, `mongle-baseline-mysql`, `mongle-baseline-redis`를 실행 상태로 남겼다. FastAPI는 종료 상태다. 일반 dev 서버 세션의 생존을 영구 보장하는 서비스 등록은 하지 않았다. 재접속 시 health부터 확인한다.

## 다음 단계 판단

**READY — RunPod mock provider 설계·구현에 착수할 수 있다. 전체 AI flow 성공 판정은 보류한다.**

로컬 FE/BE/DB/broker/worker가 실제로 동작하고, 교체 지점·입출력·실패 경로가 코드로 확인되었다. mock 단계에 AI의 config validation과 BE↔AI 서비스 키/주소 연결도 포함해야 한다. mock을 위해 운영 RunPod 키나 S3 계정을 먼저 복구할 필요는 없다.

대표 flow는 요청에 따라 아직 제출하지 않았으므로, mock 도입 후 최초 E2E에서 새 문제가 드러날 수 있다. 다음 단계 최소 범위는 [runpod-boundary.md](runpod-boundary.md)에 별도로 제안했으며 아직 구현하지 않았다.
