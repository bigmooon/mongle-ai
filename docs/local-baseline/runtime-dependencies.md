# Runtime dependencies & environment audit

## 2026-09-29 mock 구현 후 갱신

최종 후속 결과: 사진 입력도 실제 브라우저 업로드 → mock 생성 → 미리보기 → 입주까지 PASS. 텍스트/사진 job 2개 CONSUMED를 확인한 후 진단 계정·DB 행·S3 객체 5개를 정리했다. AWS 로그인 만료는 재로그인으로 해결했다.

`IMAGE_PROVIDER=mock`과 기존 fake persona 조합을 구현했다. 실제 브라우저의 텍스트 캐릭터 생성 → Redis/Celery → FastAPI mock → 실제 S3 → 미리보기 → 입주/CONSUMED까지 통과했다. provider 기본값·RunPod adapter·FE polling은 유지했다. 상세 실행법은 `mongle-ai/docs/local-character-mock.md`, 최신 검증/남은 항목은 `local-baseline.md`의 최상단 항목을 따른다. 아래의 “미구현/미검증/AI 기동 실패”는 최초 감사 당시 이력이다.

## 최신 재검증 — 2026-09-28

기존 서비스는 실행 중이므로 중복 시작/재시작하지 않았다. FE/Django HTTP 200, MySQL 미적용 migration 0, Redis I/O, Celery pong 확인. 실행 중 Django의 실제 로그인 및 업로드 API가 S3 presigned PUT/GET까지 성공했으므로 이 프로세스의 S3 설정 반영도 확인됐다. 임시 사용자와 파일은 검사 후 삭제했다.

현재 환경변수 보정(아래 최초 감사 표보다 우선):

| Variable | Used by | Required locally? | External dependency | Present? |
|---|---|---|---|---|
| AWS_PROFILE | BE/AI boto3 credential chain | 현재 인증 방식에서 Yes | AWS CLI 로그인 | Yes; mongle-dev |
| AWS_S3_BUCKET | BE/AI S3 | S3 사용 시 Yes | S3 | Yes |
| AWS_S3_PREFIX | BE/AI S3 | default 가능 | S3 | Yes |
| AWS_S3_REGION | BE S3 | default 가능 | S3 | Yes |
| AWS_REGION | AI S3 | S3 사용 시 Yes | S3 | Yes |
| AWS_S3_PRESIGNED_URL_EXPIRY | BE S3 | default 가능 | S3 | Yes |
| STORAGE_BACKEND | AI | provider 선택 | S3 | Yes; s3 |
| AWS_ACCESS_KEY_ID / AWS_SECRET_ACCESS_KEY | 명시적 키 방식 | No; 프로필 인증 사용 | AWS | .env에 저장하지 않음 |
| MONGLE_API_KEY / QWEN_BASE_URL / QWEN_MODEL / LORA_DIR | 현재 AI 기본 분기 | 현재 기동에 필요 | 내부 인증 / 모델 | No; 현재 config 검사 실패 |

프런트엔드 AWS 키는 필요 없다. 실행 명령과 다른 환경변수의 코드 위치는 아래 감사 내용을 따른다.

## 2026-09-28 업로드 후속 검사 실행 상태

01:06 KST 기준: 기존 MySQL·Redis 컨테이너는 계속 실행 중이며, 내려가 있던 Django·Celery·Frontend를 아래 명령으로 시작했다. 재설치·migration 적용·`.env` 수정은 필요하지 않았다. AWS `mongle-login` 및 `mongle-dev` STS 인증 성공; 재로그인 불필요. AI와 Beat는 시작하지 않았다.

```bash
# mongle-server에서 실행 (Django와 Celery는 각각 별도 터미널)
DATABASE_URL=mysql://root@127.0.0.1:3306/mongle \
  .venv/bin/python manage.py runserver 127.0.0.1:8000 --noreload
DATABASE_URL=mysql://root@127.0.0.1:3306/mongle \
  .venv/bin/celery -A config worker --pool=solo --concurrency=1 \
  --hostname=baseline@localhost --loglevel=info

# mongle-web에서 실행
npm run dev -- --host 127.0.0.1 --strictPort
```

이번 실행 stdout/stderr는 각각 `/tmp/mongle-upload-django.log`, `/tmp/mongle-upload-celery.log`, `/tmp/mongle-upload-vite.log`로 보냈다. 로그를 공유하기 전 인증정보 및 서명 URL 포함 여부를 확인한다. 일반 개발 프로세스로 실행했으므로 다음 접속 시 health와 worker ping을 재확인한다.

실제 브라우저 검사는 계정 0건인 진단 DB의 로그인 경계에서 중단되었다. 파일 선택은 로컬 미리보기이며 S3 PUT은 생성 작업 제출과 연속 실행되는 기존 구조다. 생성 요청 금지 범위에서 업로드 E2E는 미검증으로 남겼다. 자세한 결과는 [local-baseline.md](local-baseline.md)의 최신 후속 검증 항목을 따른다. 아래 2026-09-26 환경변수 표와 실패 기록은 당시 이력이며, S3의 현재 상태를 나타내지 않는다.

2026-09-26 검사. 모든 명령은 별도 표기가 없으면 `/Users/jpaper/Documents/projects/mong-studio`에서 시작한다. 이번 실행은 manifest/lock 변경 없이 복원했다. `.env.example`의 존재는 실제 환경변수 설정으로 세지 않는다.

## 설치

### Frontend

```bash
cd /Users/jpaper/Documents/projects/mong-studio/mongle-web
npm ci --ignore-scripts --no-audit --no-fund --cache /tmp/mongle-baseline-npm-cache
npm run build
npm run dev -- --strictPort
```

```text
Command: npm run dev -- --strictPort
Port: 127.0.0.1:5173
Required env: 없음; VITE_API_BASE 미설정/빈 값이면 로컬 proxy 사용
Dependencies: Node 24.12.0, npm, package-lock.json; API는 Django 8000
Status: PASS — typecheck/build, 페이지, 브라우저 console, API proxy
```

`--ignore-scripts`는 설치 시 Husky의 Git hook 변경을 피하기 위한 진단 옵션이다. package-lock 버전 그대로 설치했고 실제 build까지 확인했다. build의 chunk-size 경고는 그대로 남겼다. API base에 `/api/v1`을 넣으면 client가 다시 붙이므로 base는 origin 또는 빈 값이다.

### Backend

```bash
cd /Users/jpaper/Documents/projects/mong-studio/mongle-server
UV_CACHE_DIR=/tmp/mongle-baseline-uv-cache uv sync --locked --extra dev
DATABASE_URL=mysql://root@127.0.0.1:3306/mongle .venv/bin/python manage.py check
DATABASE_URL=mysql://root@127.0.0.1:3306/mongle .venv/bin/python manage.py migrate --noinput
DATABASE_URL=mysql://root@127.0.0.1:3306/mongle .venv/bin/python manage.py runserver 127.0.0.1:8000 --noreload
```

```text
Command: 위 runserver (원래 Makefile: make runserver → 0.0.0.0:8000)
Port: 127.0.0.1:8000
Required env: 이번 MySQL 진단에는 DATABASE_URL; REDIS_URL은 코드 기본값 사용
Dependencies: Python 3.12+, uv.lock, mysqlclient 빌드용 MySQL client/pkg-config, DB/Redis
Status: PASS
```

`make install-dev`는 `uv sync --locked --extra dev` 뒤 hook도 설치하므로 이번에는 sync만 직접 실행했다. Python 3.12.12를 uv가 선택했다. mysqlclient 2.2.8 native build도 성공했다. 이 머신에는 Homebrew MySQL client가 있었다. `make lint`, `make format`, `make validate`는 소스를 자동 수정하므로 실행하지 않았다.

### Database

```bash
docker run -d --name mongle-baseline-mysql \
  -p 127.0.0.1:3306:3306 \
  -e MYSQL_ALLOW_EMPTY_PASSWORD=yes -e MYSQL_DATABASE=mongle mysql:9.7
```

```text
Type: MySQL 9.7.0 (저장소 compose와 같은 mysql:9.7 이미지)
Startup method: 위 진단 전용 Docker container; 기존 동명 container가 있으면 docker start 사용
Migration command: DATABASE_URL=mysql://root@127.0.0.1:3306/mongle .venv/bin/python manage.py migrate --noinput
Status: PASS — 미적용 0, makemigrations --check --dry-run 정상, 쓰기/조회/rollback
```

진단용 DB는 운영 데이터가 없는 새 DB다. 단순 기동보다 migration 준비가 늦을 수 있으므로 `docker exec mongle-baseline-mysql mysqladmin ping` 성공 뒤 migrate한다. 비밀번호 없는 root와 loopback binding은 이번 폐기 가능한 진단 구성만을 재현한다.

Django 기본 SQLite fallback도 코드에 존재한다. `DATABASE_URL`을 생략하면 `mongle-server/db.sqlite3`를 사용한다. **SQLite I/O/migration은 이번에 검증하지 않았다.**

### Redis / broker

```bash
docker run -d --name mongle-baseline-redis -p 127.0.0.1:6379:6379 redis:7-alpine
```

```text
Startup method: 위 전용 Docker container; 다시 시작은 docker start mongle-baseline-redis
Port: 127.0.0.1:6379
Broker/result/cache: redis://localhost:6379/0 (코드 기본값)
Status: PASS — Django cache set/get/delete, worker 연결, task result
```

### Celery / worker

```bash
cd /Users/jpaper/Documents/projects/mong-studio/mongle-server
DATABASE_URL=mysql://root@127.0.0.1:3306/mongle \
  .venv/bin/celery -A config worker --loglevel=info \
  --pool=solo --concurrency=1 --hostname=baseline@localhost
```

```text
Command: 위 명령 (원래: make celery)
Broker: REDIS_URL → CELERY_BROKER_URL
Result backend: 같은 REDIS_URL
Task modules: apps.characters.tasks, apps.posts.tasks, apps.todos.tasks, apps.users.tasks
Status: PASS — 실제 process worker가 task를 수신하고 SUCCESS 반환
```

macOS 감사에서는 `solo`를 사용했다. 운영 prefork concurrency를 검증한 것은 아니다. Beat는 즉시 AI job에 필요하지 않아 실행하지 않았다. 원래 scheduler 명령은 `make celery-beat`이며 DB-backed scheduler를 쓴다.

### AI API — 실제 기동 실패 보존

GPU dependencies 전체를 설치하지 않고 저장소 Dockerfile의 `requirements-api.txt` 경로를 사용했다. 버전 이동을 막기 위해 `uv.lock`을 constraints로 사용했다.

```bash
cd /Users/jpaper/Documents/projects/mong-studio/mongle-ai
UV_CACHE_DIR=/tmp/mongle-baseline-uv-cache uv venv --python 3.12 .venv
UV_CACHE_DIR=/tmp/mongle-baseline-uv-cache uv export --frozen --no-hashes \
  --no-dev --no-emit-project --format requirements-txt \
  --output-file /tmp/mongle-ai-lock-constraints.txt
UV_CACHE_DIR=/tmp/mongle-baseline-uv-cache uv pip install --python .venv/bin/python \
  -r requirements-api.txt -c /tmp/mongle-ai-lock-constraints.txt
.venv/bin/uvicorn api.main:app --host 127.0.0.1 --port 8010
```

```text
Command: .venv/bin/uvicorn api.main:app --host 127.0.0.1 --port 8010
Port: 8010 (시작 실패하여 LISTEN 없음)
Required env: MONGLE_API_KEY + provider별 설정 (아래 표)
Dependencies: API-only Python 3.12.12 venv; 외부 AI 및 storage는 선택한 provider에 따라 필요
Status: FAIL — MissingEnvError: MONGLE_API_KEY, QWEN_BASE_URL, QWEN_MODEL, LORA_DIR
```

설치만 성공했으며 정상 AI process로 간주하지 않는다. 가짜 RunPod credential/endpoint, 임의 LoRA 경로, mock으로 config 검사를 통과시키지 않았다. `uv run`은 pyproject 전체 ML dependency sync를 유발할 수 있어 API-only venv의 binary를 직접 사용한다.

기존 full environment 설치 방법은 `uv sync`이지만 이번에는 GPU 환경/모델을 복원하지 않았다. 기존 AI compose는 `mongstudio/mongle-ai:${IMAGE_TAG:-latest}` 이미지를 받아 `.env`를 주입하는 방식이며 local source build가 아니다. 해당 compose는 실행하지 않았다.

## 기존 Docker Compose 경로 (코드 확인, 전체 실행 미검증)

`mongle-server/docker-compose.yml`: web + worker + mysql:9.7 + redis:7-alpine. `.env`의 MYSQL 변수로 DB URL을 만들고 web/worker에는 service DNS `db`, `redis`를 쓴다. 호스트에서 실행하는 이번 DB URL과 혼용하지 않는다.

```bash
cd /Users/jpaper/Documents/projects/mong-studio/mongle-server
# 실제 .env 구성 후
docker compose up --build
docker compose exec -T web python manage.py migrate
```

이번 컨테이너가 3306/6379를 사용 중이므로 동시에 같은 port의 compose를 시작하면 충돌한다. compose healthcheck는 `mysqladmin ... -uroot -proot`로 root password가 하드코딩되어 있으며, `${MYSQL_ROOT_PASSWORD}`와 불일치하면 별도 확인이 필요하다. 수정하지 않았다.

## 검사 명령

```bash
curl -i http://127.0.0.1:8000/health/
curl -i http://127.0.0.1:5173/
curl -i http://127.0.0.1:5173/api/v1/todos/
curl --max-time 3 -i http://127.0.0.1:8010/health
```

기대값: 순서대로 200, 200, **401 (미인증)**, 현재 상태에서는 connection refused. `health/`만으로 DB 정상 여부를 판단하지 않는다.

BE 디렉터리에서 아래로 DB와 worker 검사를 재현할 수 있다. 새 진단 DB에서만 실행한다.

```bash
DATABASE_URL=mysql://root@127.0.0.1:3306/mongle .venv/bin/python - <<'PY'
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
import django
django.setup()
from django.db import connection, transaction
from django.db.migrations.executor import MigrationExecutor
from django_celery_beat.models import IntervalSchedule
from django.core.cache import cache
from apps.users.models import RefreshToken
from apps.users.tasks import cleanup_expired_refresh_tokens
from config.celery import app
e = MigrationExecutor(connection)
print('unapplied', len(e.migration_plan(e.loader.graph.leaf_nodes())))
with transaction.atomic():
    row = IntervalSchedule.objects.create(every=12345, period='seconds')
    pk = row.pk
    print('read/write', IntervalSchedule.objects.get(pk=pk).every == 12345)
    transaction.set_rollback(True)
print('rollback', not IntervalSchedule.objects.filter(pk=pk).exists())
cache.set('mongle-baseline-health', 'ok', timeout=30)
print('cache', cache.get('mongle-baseline-health'))
cache.delete('mongle-baseline-health')
print('worker', app.control.ping(timeout=3))
assert RefreshToken.objects.count() == 0
r = cleanup_expired_refresh_tokens.delay()
print('result', r.get(timeout=15), r.state)
r.forget()
PY
```

## 종료·재시작

FE/Django/Celery를 시작한 터미널에서 Ctrl-C. 컨테이너는 다음으로 **중지**하며 삭제하지 않는다.

```bash
docker stop mongle-baseline-mysql mongle-baseline-redis
# 재시작
docker start mongle-baseline-mysql mongle-baseline-redis
```

감사 종료 시에는 실행 상태로 남겼다. 재시작 후 MySQL 준비 확인 → Django → worker → FE 순으로 위 명령을 실행한다. AI는 환경 미구성 상태라는 원래 실패를 그대로 재현한다.

## 환경변수 감사 원칙

세 저장소에는 `.env.example`만 있고 실제 `.env`/`.env.local`은 없었다. 코드에서 참조한 변수 중 inherited process의 nonempty 값도 없었다. 이번 BE/worker 명령에만 `DATABASE_URL`을 주입했다. `Present=No`여도 코드 기본값이 있으면 실행 가능하다. 아래 표는 값·키·endpoint 식별자를 노출하지 않는다.

소스: BE `config/settings/base.py`, `production.py`, `manage.py`, `config/celery.py`, seed command; AI `api/config.py`, `api/deps.py`, `api/security.py`, observability/storage/debug 모듈; FE `src/shared/api/client.ts`, auth/share 모듈. 추가 offline/배포 변수는 마지막 표에 분리했다.

### 로컬 서비스 및 내부 연결

| Variable | Used by | Required locally? | External dependency | Present? |
|---|---|---|---|---|
| DATABASE_URL | BE DB | MySQL 선택 시 Yes; 없으면 SQLite | local DB | 최초 No → 검사 process에 Yes |
| REDIS_URL | BE cache/Celery broker/result | 유효한 연결 필요, default 있음 | local Redis | No; default 사용 |
| DJANGO_SETTINGS_MODULE | manage.py/Celery/WSGI/ASGI | entry 기본값 있음 | 없음 | No; entry가 설정 |
| DJANGO_SECRET_KEY | Django/JWT | dev default 있음; production 필수 | 없음 | No; dev default 사용 |
| DJANGO_DEBUG | Django | No, default False | 없음 | No |
| DJANGO_ALLOWED_HOSTS | Django | local 기본값 있음 | 없음 | No |
| DJANGO_CORS_ALLOWED_ORIGINS | Django corsheaders | proxy 경로는 추가값 불필요 | 없음 | No |
| VITE_API_BASE | FE Axios/asset URL | No, 상대경로 default | BE | No |
| BASE_URL | Vite built-in / RouteGate | 직접 env 설정 불필요 | 없음 | Vite 제공 |
| MONGLE_AI_API_BASE | BE TODO/planner/quest client | 해당 기능 필요; default 8010 | AI API | No; default 사용 |
| MONGLE_AI_API_KEY | BE TODO/planner/quest 인증 | 해당 기능 Yes | AI API | No |
| MONGLE_AI_TIMEOUT_SECONDS | BE client | No; default 150초 | AI API | No |
| AI_SERVICE_URL | BE character worker | 캐릭터 Yes; 기본 빈 값 | AI API | No |
| AI_SERVICE_TOKEN | BE character worker | 캐릭터 Yes; 기본 빈 값 | AI API | No |
| MONGLE_API_KEY | AI `AppConfig`/require_api_key | **AI 기동 필수** | 내부 서비스 인증 | No |
| MONGLE_CORS_ORIGINS | AI CORS | No; 코드 defaults | 없음 | No |
| MYSQL_DATABASE | BE compose | compose 사용 시 Yes | local MySQL | No; standalone Docker에서 주입 |
| MYSQL_USER | BE compose | compose 사용 시 Yes | local MySQL | No |
| MYSQL_PASSWORD | BE compose | compose 사용 시 Yes | local MySQL | No |
| MYSQL_ROOT_PASSWORD | BE compose | compose 사용 시 Yes | local MySQL | No |

`API_BASE_URL`, `REDIS_HOST`, `DATABASE_HOST`라는 이름을 가정하지 않는다. 현행 코드의 실제 이름은 위와 같다. `CELERY_BROKER_URL`/`CELERY_RESULT_BACKEND`는 이 설정에서 `REDIS_URL`로부터 만들어지는 Django setting이다.

### AI provider와 storage

| Variable | Used by | Required locally? | External dependency | Present? |
|---|---|---|---|---|
| LLM_PROVIDER | AI character/todo/reply 선택 | 기본 qwen, 선택값 필요 | Qwen/RunPod/기존 일부 fake | No |
| QUEST_LLM_PROVIDER | AI quest | 기본 qwen | Qwen/RunPod/fake | No |
| FEED_LLM_PROVIDER | AI feed | 기본 qwen | Qwen/RunPod/fake | No |
| QWEN_BASE_URL | AI config/builders | qwen 분기 선택 시 **기동 필수** | OpenAI-compatible LLM | No |
| QWEN_MODEL | AI config/builders | qwen 분기 선택 시 **기동 필수** | 모델 | No |
| QWEN_API_KEY | AI Qwen client | 서버 인증 조건부; default EMPTY | LLM | No |
| QWEN_PERSONA_MODEL | AI character | No; QWEN_MODEL fallback | LLM | No |
| QWEN_STRUCTURED_MODE | AI TODO | No; default vllm | LLM | No |
| PLANNER_OPENAI_BASE_URL | AI planner override | 선택사항; model과 쌍 | OpenAI-compatible API | No |
| PLANNER_OPENAI_MODEL | AI planner override | 선택사항; base와 쌍 | 모델 | No |
| PLANNER_OPENAI_API_KEY | AI planner override | 선택 API 인증 시 필요 | 외부/로컬 LLM | No |
| IMAGE_PROVIDER | AI image/BE legacy settings | AI 기본 local | local ML/RunPod | No |
| LORA_DIR | AI config/local image | IMAGE_PROVIDER=local이면 **기동 필수** | 모델 파일/local ML | No |
| RUNPOD_API_KEY | AI adapters/BE legacy settings | RunPod 선택 시 필요; 기본 health 불필요 | RunPod | No |
| RUNPOD_PLANNER_ENDPOINT_URL | AI TODO/planner | LLM_PROVIDER=runpod이면 필수 | RunPod | No |
| RUNPOD_CHARACTER_ENDPOINT_URL | AI persona/quest/feed/reply | 관련 provider=runpod이면 필수 | RunPod | No |
| RUNPOD_IMAGE_ENDPOINT_URL | AI image | URL 또는 ID 필요 | RunPod | No |
| RUNPOD_IMAGE_ENDPOINT_ID | AI image/BE legacy | URL 없을 때 대안 | RunPod | No |
| RUNPOD_IMAGE_GEN_V2_ENDPOINT_ID | AI image | ID fallback | RunPod | No |
| RUNPOD_TIMEOUT_SECONDS | BE legacy image settings | 현재 대표 flow에서 미사용 | RunPod | No |
| STORAGE_BACKEND | AI API storage factory | No; default local | S3/local | No |
| STORAGE | AI `adapters/_shared/storage.py` 별도 factory | API의 STORAGE_BACKEND 대체값 아님 | S3/local | No |
| LOCAL_STORAGE_ROOT | AI config/source bytes fetch | No; 기본 경로 있음 | local files | No |
| AWS_S3_BUCKET | BE/AI S3 | S3 사용할 때 Yes | S3 | No |
| AWS_S3_PREFIX | BE/AI namespace | No; default 있음 | S3/local | No |
| AWS_S3_REGION | BE S3 | No; default 있음 | S3 | No |
| AWS_REGION | AI S3 config | STORAGE_BACKEND=s3이면 **기동 필수** | S3 | No |
| AWS_S3_PRESIGNED_URL_EXPIRY | BE S3 | No; default 3600초 | S3 | No |
| AWS_ACCESS_KEY_ID | BE boto3 credentials | S3 인증 조건부; SDK credential chain 가능 | AWS | No |
| AWS_SECRET_ACCESS_KEY | BE boto3 credentials | 위와 쌍/SDK chain | AWS | No |

RunPod 키를 BE에만 넣어도 AI 프로세스로 전달되지 않는다. BE와 AI는 독립된 환경이다. S3도 BE는 `AWS_S3_REGION`, AI는 `AWS_REGION`이라는 차이가 있다. AWS SDK의 profile/role/session credential 유효성은 검사하지 않았다. 버킷 미설정 guard 때문에 이번 검사는 AWS 네트워크에 도달하지 않았다.

`LLM_PROVIDER=fake`가 TODO 전체의 mock 스위치는 아니다. `_build_todo_llm`은 RunPod/특정 OpenAI override 외에는 QWEN_BASE_URL/MODEL을 요구한다. 현재 example의 fake LLM은 이미지 RunPod/S3까지 제거하지 않는다.

### 현재 baseline에 필요 없는 기능 설정

| Variable | Used by | Required locally? | External dependency | Present? |
|---|---|---|---|---|
| EMAIL_BACKEND | BE email | No; console 기본 | SMTP 선택 가능 | No |
| EMAIL_HOST | BE email | SMTP 선택 시 | SMTP | No |
| EMAIL_PORT | BE email | default 587 | SMTP | No |
| EMAIL_USE_TLS | BE email | default True | SMTP | No |
| EMAIL_HOST_USER | BE email | SMTP 인증 시 | SMTP | No |
| EMAIL_HOST_PASSWORD | BE email | SMTP 인증 시 | SMTP | No |
| DEFAULT_FROM_EMAIL | BE email | default 있음 | SMTP/console | No |
| KAKAO_REST_API_KEY | BE OAuth | 카카오 로그인만 | Kakao | No |
| KAKAO_CLIENT_SECRET | BE OAuth | 설정에 따라 조건부 | Kakao | No |
| KAKAO_REDIRECT_URI | BE OAuth | 카카오 로그인만 | Kakao | No |
| VITE_KAKAO_CLIENT_ID | FE OAuth | 카카오 로그인만 | Kakao | No |
| VITE_KAKAO_REDIRECT_URI | FE OAuth | 카카오 로그인만 | Kakao | No |
| VITE_KAKAO_JS_KEY | FE share | 카카오 공유만 | Kakao | No |
| LANGSMITH_TRACING | AI observability | No | LangSmith | No |
| LANGSMITH_API_KEY | AI observability | tracing 선택 시 | LangSmith | No |
| LANGSMITH_ENDPOINT | AI observability | No; 초기화 default | LangSmith | No |
| LANGSMITH_PROJECT | AI observability | No; 초기화 default | LangSmith | No |
| MONGLE_DEBUG_TODO | AI logging | No | 없음 | No |
| MONGLE_DEBUG_CHARACTER | AI logging | No | 없음 | No |
| SEED_IMAGE_BASE_URL | BE seed command | seed 전용 | 선택 image host | No |
| SEED_DEMO_IMAGE_URL | BE seed dynamic env lookup | seed 전용 | 선택 image host | No |
| SEED_ADMIN_IMAGE_URL | BE seed dynamic env lookup | seed 전용 | 선택 image host | No |
| SEED_SUPERUSER_PASSWORD | BE seed command | seed 전용 | 없음 | No |

### GPU·학습·배포용 변수 (local API baseline에서는 전부 불필요)

이 표의 묶음은 같은 파일/용도의 변수들이다. 코드 직접 읽기 및 동적 lookup mapping을 함께 확인했다. 값은 기록하지 않는다. 로컬 inherited process에서는 모두 미설정이며 CI secret의 원격 존재 여부는 조회하지 않았다.

| Variables | Used by / source | External dependency | Present? |
|---|---|---|---|
| HF_HOME, HF_TOKEN | `runpod_workers/llm/{pipeline,bake}.py`, image bake | HF 모델/cache | No |
| LLM_BASE_MODEL, LLM_BASE_MODEL_REVISION | LLM pipeline/bake | 모델 | No |
| LORA_PLANNER_REPO, LORA_CHARACTER_REPO, LORA_QUEST_REPO, LORA_REPLY_REPO, LORA_FEED_REPO | LLM pipeline `_ADAPTER_ENV` 동적 lookup | HF LoRA | No |
| SDXL_BASE_MODEL, SDXL_BASE_MODEL_REVISION | image `model_refs.py` | HF 모델 | No |
| CONTROLNET_CANNY_MODEL, CONTROLNET_CANNY_MODEL_REVISION | image `model_refs.py` | HF 모델 | No |
| LCM_LORA_SOURCE, LCM_LORA_REVISION | image `model_refs.py` | HF LoRA | No |
| QWEN2VL_MODEL, QWEN2VL_MODEL_REVISION, QWEN25VL_MODEL, QWEN25VL_MODEL_REVISION | image `model_refs.py` | HF VLM | No |
| CHAR_LORA_SOURCE, MASCOT_LORA_SOURCE | image_character runtime/stage | HF LoRA | No |
| LOG_LEVEL, MAX_UPLOAD_BYTES, RETURN_DEBUG_DEFAULT, MAX_INPUT_PIXELS, PRELOAD_MODELS, MODEL_CACHE_MODE | image worker handlers/pipeline | GPU runtime | No |
| MAX_PERSONA_LENGTH, MAX_QUEST_LENGTH | text_character/feed handlers | GPU runtime | No |
| HF_HUB_DISABLE_SYMLINKS_WARNING | feed pipeline | 없음 | 코드에서 설정 |
| RUNPOD_ENDPOINT_ID | image_character/example_client.py | RunPod example | No |
| API_DOCKER_IMAGE, POD_NAME, CPU_FLAVOR, VCPU_COUNT | `runpod_workers/setup_pod.py` | 배포 제어 | No; 실행하지 않음 |
| LORA_REPO_ID | `scripts/outlines_poc/run.py` | HF 실험 | No |
| OPENAI_API_KEY | `sft_pipeline/build/lib/rephrase.py` | 데이터 생성용 OpenAI | No |
| IMAGE_TAG | AI compose | container registry | No; default latest |
| AWS_ROLE_ARN, AWS_REGION, S3_BUCKET, CLOUDFRONT_DISTRIBUTION_ID | FE deploy workflow secrets | AWS 배포 | local No / CI 미확인 |

API-only 설치에는 GPU 모델·vLLM·torch·diffusers를 넣지 않았다. 모델 파일의 존재/정합성 및 GPU 실행은 이번 PASS 범위 밖이다.

## 2026-09-28 S3 로컬 연결 추가

AWS CLI 로그인 프로필 `mongle-login`을 만들고, SDK용 `mongle-dev` 프로필에 아래 값을 설정했다. 로그인 세션이 만료되면 `aws login --profile mongle-login`을 다시 실행한다.

```ini
[profile mongle-dev]
region = ap-northeast-2
credential_process = /opt/homebrew/bin/aws configure export-credentials --profile mongle-login --format process
```

`mongle-server/.env` (gitignored, 새로 생성):

```dotenv
AWS_PROFILE=mongle-dev
AWS_S3_BUCKET=mongle-dev-asset
AWS_S3_REGION=ap-northeast-2
AWS_S3_PREFIX=mongle-village
AWS_S3_PRESIGNED_URL_EXPIRY=600
```

`mongle-ai/.env` (gitignored, 새로 생성):

```dotenv
AWS_PROFILE=mongle-dev
STORAGE_BACKEND=s3
AWS_S3_BUCKET=mongle-dev-asset
AWS_REGION=ap-northeast-2
AWS_S3_PREFIX=mongle-village
```

이 설정은 호스트 Mac의 Python 프로세스용이다. Docker 컨테이너에 호스트 프로필이나 `/opt/homebrew/bin/aws`가 자동 전달되지는 않는다. S3 관련 설정만 추가했으며 DB/AI 필수 환경변수는 기존 실행 지침에 따라 별도로 제공해야 한다. 실행 중인 Django/Celery/AI 프로세스는 재시작 후 새 설정을 읽는다. 실제 S3 검증 결과는 `local-baseline.md`의 후속 검증 항목에 기록했다.
