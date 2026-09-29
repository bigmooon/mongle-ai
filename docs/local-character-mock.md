# 로컬 캐릭터 mock 실행

캐릭터 생성 연결 검증 전용이다. 기존 `FakeLLM`과 새 `MockImageGenerator`를 조합한다. 이미지 mock은 입력 사진/설명을 분석하지 않고 64×64 보라색 체크무늬 PNG를 반환한다. `appearance_payload`는 `None`이다. 실제 AI 품질이나 RunPod HTTP submit/status 동작을 검증하는 기능이 아니다.

## 설정

`mongle-ai/.env`에서 다음을 선택한다. 기존 S3 설정은 유지한다.

```dotenv
LLM_PROVIDER=fake
QUEST_LLM_PROVIDER=fake
FEED_LLM_PROVIDER=fake
IMAGE_PROVIDER=mock
STORAGE_BACKEND=s3
AWS_PROFILE=mongle-dev
AWS_S3_BUCKET=mongle-dev-asset
AWS_REGION=ap-northeast-2
AWS_S3_PREFIX=mongle-village
LANGSMITH_TRACING=false
```

`MONGLE_API_KEY`에는 로컬 서비스 간 공유 키를 설정한다. 키 값은 커밋하지 않는다. Django `.env`의 `AI_SERVICE_TOKEN`과 동일해야 하며, `AI_SERVICE_URL=http://127.0.0.1:8010`을 사용한다. 이번 로컬 환경에는 공유 키를 생성해 설정했다. TODO 쪽 `MONGLE_AI_API_BASE/KEY`도 같은 주소/키로 연결했지만 TODO mock은 구현하지 않았다.

- `LLM_PROVIDER=fake`는 캐릭터 페르소나용 기존 구현이다. TODO/플래너 전체를 mock하지 않는다.
- quest/feed를 fake로 명시해야 기본 qwen 설정 요구를 피할 수 있다. 이미지 mock은 캐릭터 `generate` 계약만 지원하며 피드 이미지 생성은 범위 밖이다.
- mock에서도 API 키와 S3 bucket/region/인증은 필요하다. GPU, LoRA, Qwen, RunPod 키는 위 조합에 필요 없다.
- RunPod endpoint는 이 조합에서 config에 로드되지 않으므로 캐릭터 warmup도 외부 RunPod에 요청하지 않는다.
- S3를 제외한 오프라인 검증에는 기존 `STORAGE_BACKEND=local`을 사용할 수 있다. 이 구현은 메모리/data URI이며 디스크 영속 저장이 아니다.

## 시작

AWS 세션이 만료되면 호스트 터미널에서 다음을 실행한다.

```bash
aws login --profile mongle-login
```

각 저장소에서 별도 터미널로 실행한다. Django/worker는 환경변수 변경 후 재시작한다.

```bash
# mongle-ai
.venv/bin/uvicorn api.main:app --host 127.0.0.1 --port 8010

# mongle-server (기존 진단 MySQL/Redis가 실행 중이어야 함)
DATABASE_URL=mysql://root@127.0.0.1:3306/mongle .venv/bin/python manage.py runserver 127.0.0.1:8000 --noreload
DATABASE_URL=mysql://root@127.0.0.1:3306/mongle .venv/bin/celery -A config worker --pool=solo --concurrency=1 --hostname=baseline@localhost --loglevel=info

# mongle-web
npm run dev -- --host 127.0.0.1 --strictPort
```

기존 프로세스가 해당 포트를 사용한다면 중복 실행하지 않는다. 호스트 프로필과 `/opt/homebrew/bin/aws`를 사용하는 현재 S3 인증 방식은 Docker 컨테이너에 자동 전달되지 않는다.

## 검증

```bash
# mongle-ai: 기존 API-only .venv + uv.lock의 pytest 개발 의존성 사용
.venv/bin/python -m pytest -o addopts='' tests/api/test_character_mock.py tests/api/test_config.py tests/api/test_deps.py tests/api/test_character.py tests/agents/character_creation tests/adapters/character_creation -q

# mongle-server: 독립 test settings/DB, 실제 AWS 호출을 대체하는 기존 단위 검사
.venv/bin/python -m pytest -o addopts='' tests/test_characters.py -q
```

이번 변경에 해당하는 선택 검사를 실행하며 전체 저장소 coverage 80% gate를 통과했다는 뜻은 아니다. 새 검사는 실제 lifespan/config/provider 조립과 job API를 사용한다. 소켓 연결을 금지한 상태로 submit 202/pending → poll done, 인증 401, 잘못된 입력 422, 없는 job 404, warmup, PNG CRC/압축 데이터, S3·인증 필수 설정을 확인한다.

브라우저에서는 정상 로그인 → 텍스트 캐릭터 생성 → 기존 polling → S3 이미지 미리보기 → 입주를 확인한다. 사진 입력은 S3 원본 업로드 → AI 원본 fetch → 같은 mock 생성으로 이어진다. 실패/취소/환불/중복 입주는 기존 Django 검사로 검증하며, 실제 외부 장애/timeout E2E와는 구분한다.

## 변경 경계

- `api/config.py`: `IMAGE_PROVIDER=mock` 허용. 기본값과 다른 provider 검증 불변.
- `api/deps.py`: mock 이미지 provider를 지연 생성해 기존 `ImageGeneratorPort`에 주입.
- `adapters/character_creation/mock_image.py`: 표준 라이브러리만 사용하는 진단 PNG.
- 기존 fake persona, S3 adapter, async job, Django/Celery, FE polling은 변경 없음.

실제 모델로 돌아갈 때는 provider와 해당 endpoint/키 또는 LoRA 설정을 명시적으로 복구하고 AI를 재시작한다. mock 결과를 실제 모델 생성물로 간주하지 않는다.

## 실행 결과 — 2026-09-29

- AI 선택 검사 152 passed, Django 캐릭터 검사 53 passed. 신규 코드 Ruff 검사 및 git diff --check 통과.
- 실제 UI 텍스트/사진 입력 모두 생성 → 기존 Redis/Celery → FastAPI mock → 실제 S3 → FE polling → 미리보기 → 입주 성공. DB job 2개 CONSUMED, 캐릭터 2건 확인.
- 사진 원본의 UPLOAD_COMPLETED 및 S3 바이트 일치 확인. 두 생성 이미지 GET 성공. 진단 PNG 표시를 실제 브라우저에서 확인.
- 정상 로그아웃 후 진단 계정과 관련 DB 행, 해당 계정의 S3 객체 5개(원본/생성/감사 로그)를 삭제하고 부재 확인.
- 중간 AWS 세션 만료는 사용자의 `aws login --profile mongle-login` 재실행으로 해결했다. 세션 만료 시 다음 검증에도 재로그인이 필요할 수 있다.
- 소스 변경은 AI provider 선택/추가와 검사·문서에 한정된다. 실제 RunPod endpoint는 호출하거나 배포하지 않았다. HTTP RunPod protocol 자체·실제 AI 품질·실서비스 장애/timeout E2E를 검증한 것은 아니다.
