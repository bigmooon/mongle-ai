# 로컬 실행 감사 인수인계 — 2026-09-29

이 디렉터리는 상위 `mong-studio` 작업 공간에서 진행한 FE/BE/AI 통합 감사의 버전 관리 스냅샷이다. 상위 폴더 자체는 Git 저장소가 아니므로 AI 포크에 문서 5개와 후속 프롬프트를 함께 보존한다. 문서의 `mongle-ai/`, `mongle-server/`, `mongle-web/` 경로는 세 저장소가 나란히 있는 workspace 기준이다. 로컬 절대 경로는 당시 검사 환경을 뜻한다.

## 최초 요청과 완료 여부

| 최초 STEP | 결과 / 증거 |
|---|---|
| 1 구조 | [architecture-inventory.md](architecture-inventory.md) |
| 2 실행 방법 | [runtime-dependencies.md](runtime-dependencies.md) |
| 3 환경변수 | runtime-dependencies의 코드 기준 표 및 최신 보정 |
| 4 실행 | [local-baseline.md](local-baseline.md)의 실제 명령/결과 |
| 5 health | local-baseline의 DB/Redis/worker/브라우저 증거 |
| 6 대표 기능 | [representative-flow.md](representative-flow.md), 텍스트 캐릭터 추천 |
| 7 RunPod 경계 | [runpod-boundary.md](runpod-boundary.md), 파일/함수/계약/상태/timeout |
| 8 baseline | local-baseline, 최초 상태와 후속 상태 분리 |
| 9 mock 최소 제안 | runpod-boundary, 이후 별도 승인으로 구현 완료 |

최초 감사는 완료됐다. 그 후 사용자가 S3 연결과 캐릭터 mock 구현을 승인했고, 실제 브라우저 텍스트·사진 입력 생성/입주까지 통과했다. 이는 provider mock + 실제 앱/S3 경로의 성공이며, 실제 RunPod adapter/HTTP transport나 모델 품질의 검증은 아니다.

## 다음 작업과 범위

[새 세션용 프롬프트](next-session-prompt.md)를 사용해 **캐릭터 실패/취소/timeout 경로 감사**만 진행한다. TODO/플래너/피드 확대, RunPod 복구는 최초 요청의 미완료 항목이 아니라 별도 선택 작업이다.

현재 실행법: [local-character-mock.md](../local-character-mock.md). 테스트 계정과 S3 진단 객체는 정리됐으므로 기존 계정으로 로그인할 수 있다고 가정하지 않는다. 서비스와 AWS 로그인은 새 세션에서 재확인한다.

현재 성공 증거: AI 선택 검사 152개, Django 캐릭터 53개; 브라우저 job 2개 CONSUMED. 전체 repository CI/coverage gate의 성공 판정은 아니다.

PR은 `bigmooon/mongle-ai` 포크의 `chore/local-character-mock-baseline` → 같은 포크 `main`으로만 생성한다. main에 API 변경이 병합되면 기존 배포 workflow가 실행될 수 있으므로 자동 merge하지 않는다. `.env`와 인증정보는 이 스냅샷에 포함하지 않는다.
