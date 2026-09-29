# 다음 세션: 캐릭터 mock 실패 경로 감사

당신은 기존 AI 서비스의 로컬 실행 기준선을 검증하는 엔지니어다. 이전 감사나 mock 구현을 처음부터 반복하지 말고, 아래 인수인계 상태를 확인한 뒤 이번 범위만 수행한다.

## 작업 위치와 먼저 읽을 문서

작업 공간: `/Users/jpaper/Documents/projects/mong-studio`
이 폴더 아래 `mongle-ai`, `mongle-server`, `mongle-web`은 독립 Git 저장소다.

1. 각 저장소의 `AGENTS.md` 및 작업에 해당하는 지침. AI의 피처 AGENTS.md 경로가 없으면 실제 `docs/features/character_generation/CLAUDE.md`를 확인한다.
2. `mongle-ai/docs/local-baseline/README.md`
3. 같은 디렉터리의 `local-baseline.md`, `architecture-inventory.md`, `runtime-dependencies.md`, `representative-flow.md`, `runpod-boundary.md`
4. `mongle-ai/docs/local-character-mock.md`
5. AI `api/config.py`, `api/deps.py`, `adapters/character_creation/mock_image.py`, `tests/api/test_character_mock.py`
6. BE `apps/characters/tasks.py`, `views.py`, `tests/test_characters.py`와 FE character 생성/polling 코드

상위 작업 공간에도 감사 문서 5개의 로컬 원본이 있다. 저장소 문서는 2026-09-29 인수인계 스냅샷이다. 최신 날짜의 실행 증거를 우선하고, 과거 FAIL/미구현 기록을 현재 상태로 해석하지 않는다.

## 완료된 작업 — 다시 구현하지 말 것

- 최초 요청 STEP 1–9(구조/실행 명령/환경변수/health/대표 flow/RunPod 경계/기준선/mock 제안) 완료.
- 후속 사용자 승인으로 캐릭터 mock 구현 완료: 기존 `LLM_PROVIDER=fake` + 새 `IMAGE_PROVIDER=mock`. 고정 64×64 진단 PNG를 반환하며 실제 이미지 생성/사진 분석은 하지 않는다.
- FE, Django, MySQL, Redis, Celery, FastAPI 및 실제 S3를 연결했다.
- 실제 브라우저에서 텍스트·사진 입력 모두 생성 → Redis/Celery → FastAPI mock → S3 → 기존 polling → 미리보기 → 입주를 확인했다. DB job 2개 CONSUMED 및 캐릭터 2건을 확인했다.
- 원본 사진 S3 바이트 일치, 생성 이미지 조회 확인. 진단용 계정/관련 DB 행/S3 객체 5개는 삭제 완료했다. 기존 진단 로그인 계정은 이제 없다.
- AI 선택 검사 152개, BE 캐릭터 검사 53개 통과. 전체 저장소 coverage gate 통과와는 구분한다.
- 실제 RunPod endpoint/HTTP submit/status, GPU 모델 품질은 미검증이다. provider mock이 RunPod transport를 통과했다고 주장하지 말 것.

## 이번 목표

캐릭터의 **실패·취소·timeout·중복 요청 처리**에 대한 재현 가능한 로컬 기준선을 만든다. 성공 흐름 확대나 TODO/플래너/피드 mock 도입은 이번 범위가 아니다.

### 진행 순서

1. git status/현재 브랜치/최근 변경을 확인하고 기존 작업을 보존한다. 서비스 health, DB, Redis, worker 연결, AWS 인증을 현재 시점에서 확인한다. 살아 있는 서버를 중복 실행하지 않는다.
2. 기존 코드와 테스트를 읽어 실제 상태 전이·재시도·환불 정책을 표로 정리한다. `Celery SUCCESS`와 `application SUCCEEDED`를 구분하고, 선언된 max_retries를 실제 자동 재시도로 추정하지 않는다.
3. 다음 시나리오의 기존 검사 여부와 실측 여부를 분리한다.
   - AI 오류 → job FAILED → FE 오류 표시
   - QUEUED/IN_PROGRESS 취소 → 후속 성공 결과 폐기 여부 → 생성 횟수 복구
   - AI 응답 지연/timeout → BE job 상태 및 FE polling 종료/재개 동작
   - 완료된 job의 중복 입주 → 거부 및 Character 중복 없음
   - 가능하면 S3 저장 실패 → 상태/정리/고아 객체 여부
4. 기존 테스트 및 일회성 진단 하네스로 가능한 검증부터 수행한다. 실제 재현에 필요하다면 로컬 mock/테스트에 한정한 지연·오류 주입을 최소한으로 추가할 수 있다. 오류 주입은 명시적 opt-in, 기본 성공 동작 불변, 외부 유료 호출 없음, 실행 후 원복이 조건이다. 사용자 입력 문자열을 숨은 실패 스위치로 사용하지 않는다.
5. 실시간 timeout/취소가 어렵다면 단위/통합 검사와 코드 근거를 기록하고 E2E 미검증으로 남긴다. 테스트에서 줄인 시간 제한을 운영 기본값으로 실측한 것처럼 표현하지 않는다.
6. 실패는 먼저 기록한다. 실제 결함을 발견해도 이번 범위를 넘어 FE/BE/DB/polling을 즉시 수정하지 말고 재현 조건·근거·영향·최소 수정 후보를 보고한다.
7. 임시 진단 계정·job·S3 객체는 생성한 범위만 추적해 정리한다. 실행 중인 사용자 작업이나 기존 파일/데이터는 건드리지 않는다. 정리 후 부재와 worker 유휴 상태를 확인한다.

### 결과 기록

`mongle-ai/docs/local-baseline/character-failure-baseline.md`에 다음 표를 작성한다.

| Scenario | Injection / command | Expected from code | Observed | FE / DB / Worker state | Cleanup | PASS / FAIL / NOT RUN | Evidence level |

최신 `local-baseline.md`에 요약을 추가한다. 상위 폴더 원본에도 동일 요약을 반영하거나 어느 문서가 최신인지 명시한다. 실행 시각, 명령, 단위/통합/실제 브라우저 구분, 잔여 차단점을 기록하고 인증정보/서명 URL은 넣지 않는다.

## 실행 환경 주의

- FE 5173, Django 8000, FastAPI 8010. 진단 MySQL 3306, Redis 6379.
- Docker 컨테이너: `mongle-baseline-mysql`, `mongle-baseline-redis`. DB URL은 실행 문서의 로컬 진단 값을 사용한다. DATABASE_URL 생략으로 SQLite에 접속하지 않도록 한다.
- `.env`는 로컬에 있으며 gitignored다. 공유 키를 출력하거나 예제 파일로 덮어쓰지 않는다.
- AI 설정은 LLM/QUEST_LLM/FEED_LLM provider=fake, IMAGE_PROVIDER=mock, STORAGE_BACKEND=s3. TODO/플래너/피드 전체 mock이 아님.
- S3: `mongle-dev-asset`, 서울 `ap-northeast-2`, prefix `mongle-village`. AWS 프로필은 로그인용 `mongle-login`, SDK용 `mongle-dev`다. 세션 만료 시 사용자에게 `aws login --profile mongle-login` 재로그인을 요청하고 비의존 작업은 계속한다.
- 기존 API-only `.venv`를 사용한다. 무심코 `uv sync`로 GPU 전체 의존성을 설치하거나 패키지/lock을 업데이트하지 않는다.
- 금지: RunPod 재배포/실제 유료 AI 호출, SSE/WebSocket 신설, polling 변경, 성능 최적화, 광범위 리팩터링, production 설정 변경.

## Git / PR 경계 — 반드시 준수

허용된 포크만 사용한다:
- `bigmooon/mongle-ai`
- `bigmooon/mongle-server`
- `bigmooon/mongle-web`

`mong-studio/*` 원본에는 push/PR/issue/comment/merge를 하지 않는다. 원격 이름만 믿지 말고 URL과 GitHub base/head 소유자를 확인한다.
현재 mock 변경은 AI 포크의 `chore/local-character-mock-baseline` 브랜치에 보존한다. 시작할 때 실제 commit/PR 상태를 조회한다. 그 브랜치에 추가 수정이 필요하면 별도 후속 브랜치로 작업하고 기존 변경을 덮어쓰지 않는다.

필요한 commit 및 draft PR 생성은 허용한다. `gh pr create --repo bigmooon/<repo>`를 명시하고 base repository도 같은 포크로 지정한다. 기본값으로 upstream PR이 열리지 않게 한다. main 직접 push, force push, PR merge, 태그/배포 workflow 실행은 하지 않는다. main merge 시 기존 배포 workflow가 실행될 수 있으므로 이번 작업에서 merge하지 않는다.
`.env`, credentials, 토큰, 서명 URL, 실제 사용자 데이터, 임시 로그는 커밋하지 않는다.

## 완료 조건

검증 가능한 시나리오가 근거와 함께 분류되고, 미검증 항목은 이유가 명확하며, 진단 데이터와 주입 설정이 정리되어야 한다. 최종 응답에는 관측된 실패/취소/timeout 동작, 수정하지 않은 발견 사항, 검사 결과, 잔여 항목, 포크에만 생성한 commit/PR을 요약한다. 새로운 기능 영역으로 자동 확장하지 않는다.
