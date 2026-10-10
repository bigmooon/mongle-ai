# 몽글마을 AI

> 애착 인형을 AI 캐릭터로 만들고, 막연한 목표를 실행 가능한 TODO와 퀘스트로 바꾸는 에이전트 서비스

[![Python](https://img.shields.io/badge/Python-3.11%2B-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115%2B-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![LangGraph](https://img.shields.io/badge/LangGraph-0.2-1C3C3C)](https://langchain-ai.github.io/langgraph/)
[![API tests](https://github.com/bigmooon/mongle-ai/actions/workflows/api-tests.yml/badge.svg?branch=main)](https://github.com/bigmooon/mongle-ai/actions/workflows/api-tests.yml)

<p align="center">
  <img src="https://raw.githubusercontent.com/bigmooon/mongle-web/main/public/assets/tutorial/village.png" alt="몽글마을 메인 화면" width="88%" />
</p>

## 프로젝트 개요

**내일도와줘, 몽글마을**은 꾸준한 기록과 루틴 관리를 원하는 사용자를 위해, **자기관리 기능과 애착 인형 기반의 정서적 연결을 결합한 서비스**입니다. 20\~30대 여성을 핵심 기획 대상으로 삼아 생산성 앱과 성인 키덜트 시장이 만나는 틈새를 겨냥했습니다. 나의 애착 인형을 픽셀 마을의 AI 주민으로 만들고, 자연어로 이야기한 목표를 실행할 TODO로 구체화합니다.

사용자는 계획을 확인하고 저장한 뒤, 자신의 할 일과 연결된 주민의 퀘스트를 함께 수행합니다. 퀘스트와 연결된 TODO를 완료하면 사과 토큰을 받고, 주민의 이미지·글이 담긴 개인 피드가 생성됩니다. 여기에 캘린더, 집중을 돕는 포모도로, 하루를 돌아보는 회고를 더해 **계획 → 실천 → 성취 기록**을 하나의 마을에서 경험하도록 구성했습니다.

몽글마을은 나만의 캐릭터와 작은 실천을 쌓으며 다시 찾아오고 싶은 자기관리 경험을 목표로 합니다. 대상 사용자와 제품의 출발점은 [프로젝트 기획서의 「핵심 목표·주요 고객」](https://drive.google.com/file/d/1AT0YGK2BfbWJpBcsvgHfugAlRHEdQTak/view)에 정리되어 있습니다.

AI는 사용자의 입력을 서비스에서 활용할 수 있는 생성 결과로 바꿉니다. 자연어 목표에서 구조화된 계획을 만들고, 캐릭터의 페르소나·퀘스트·이미지·캡션·답글을 생성합니다. FastAPI가 추론 요청을 받아 에이전트와 모델 어댑터를 실행하고, 결과의 저장과 사용자별 보상 처리는 Server에 맡깁니다.

| 영역 | 저장소 | 역할 |
| --- | --- | --- |
| Web | [mongle-web](https://github.com/bigmooon/mongle-web) | React UI와 Phaser 마을 화면 |
| Server | [mongle-server](https://github.com/bigmooon/mongle-server) | 인증·도메인 API·비동기 작업 관리 |
| AI | **현재 저장소** | LLM/VLM 에이전트와 FastAPI 추론 API |

## 문제 정의와 리서치 근거

### 1. 계획을 세우는 데서, 기록과 루틴을 이어가는 수요로

자기관리는 일상적인 관심사가 되었습니다. 잡플래닛이 2024년 발표한 설문에서는 **직장인 응답자의 71.2%, 약 10명 중 7명**이 자기개발을 하고 있다고 답했습니다. 전체 응답자는 직장인·휴직/구직자·대학생 등 323명이며, 직장인 수치는 그중 직장인 그룹의 응답입니다. [잡플래닛 조사](https://www.jobplanet.co.kr/contents/news-6416)

기획 발표 자료에서는 Better, Notein, To-Do List, 마이루틴 등 기록·루틴 앱을 최근 1년 성장률 상위 사례로 제시했습니다. 팀은 이 흐름에서 **사용자가 계획을 작성하는 기능에 더해, 꾸준히 기록하고 루틴을 관리할 경험을 찾고 있다**는 기회를 읽었습니다. 성장률의 상세 수치와 원자료 확인 범위는 [시장조사 출처 기록](docs/MARKET_RESEARCH.md)에 정리했습니다.

### 2. 핵심 기획 대상: 자기관리에 관심 있는 20\~30대 여성

코리안클릭의 2023.05\~2024.04 자료를 인용한 보도에서 스케줄 관리 앱 이용자는 **여성 55.8%**, 연령별로는 **30대 27.7%·20대 27.3%**였습니다. 팀은 여성 이용자가 더 많고 20\~30대가 합계 55.0%를 차지한다는 점에 주목해, 기록과 루틴 관리에 관심 있는 **20\~30대 여성을 핵심 기획 대상**으로 삼았습니다. 성별·연령별 비율은 각각의 분포이며, ‘20\~30대 여성의 비율이 55.0%’라는 뜻은 아닙니다. [이용자 구성 조사](https://www.banronbodo.com/news/articleView.html?idxno=22900)

### 3. 수요는 있지만, 꾸준히 돌아오기는 어렵다

높은 관심이 지속적인 사용을 보장하지는 않습니다. OneSignal의 **2024년 생산성 앱 벤치마크**에서는 **1일 리텐션 32.86%, 30일 리텐션 9.63%** 수준으로 나타났습니다. 몽글마을은 이 간극을 ‘계획을 세우게 하는 것만으로는 작심삼일을 넘기 어렵다’는 문제로 받아들였습니다. [OneSignal 벤치마크](https://onesignal.com/mobile-app-benchmarks-2024)

팀은 특히 **완료 경험이 체크 표시에서 끝나면 → 서비스에 정서적 애착을 쌓기 어렵고 → 다시 방문해 루틴을 이어갈 동기가 약해질 수 있다**고 보았습니다. 이는 리텐션 통계에서 직접 입증된 원인이 아니라, 몽글마을이 제품으로 검증하려는 문제 가설입니다. 그래서 ‘할 일을 잘 관리하는가’와 함께 ‘이 공간에 다시 오고 싶은가’를 설계 기준으로 삼았습니다.

![수요 증가, 핵심 이용자층, 지속률의 한계, 이탈 원인 가설, 몽글마을의 기획 방향을 연결한 흐름](docs/images/product-concept.svg)

### 4. 경쟁 서비스를 세 가지 접근으로 비교

기획 과정에서는 비교 대상을 **일정 관리·개인화·게이미피케이션**으로 나눴습니다. 아래 구분은 발표 자료의 비교 관점이며, 각 서비스의 전체 기능을 배타적으로 분류하거나 성능 순위를 매긴 것은 아닙니다.

| 접근 | 비교한 서비스 | 팀이 주목한 경험 |
| --- | --- | --- |
| 일정 관리 | Todoist · TickTick · Microsoft To Do | 할 일, 마감일, 반복 일정을 체크리스트로 관리 |
| 개인화 | Notion | 문서·데이터베이스·일정 화면을 자신에게 맞게 구성 |
| 게이미피케이션 | Habitica · gogh · Cram & Conquer | 아바타·공간·퀘스트·보상으로 목표 수행에 재미를 부여 |

이 비교에서 몽글마을이 찾은 기회는 **자기관리 기능의 실용성과 캐릭터에 대한 개인적인 애착을 함께 강화하는 것**이었습니다. 게임형 보상에 더해, 사용자가 이미 아끼는 인형을 주민으로 만들면 서비스 밖의 애착을 일상 관리 경험으로 이어올 수 있다고 보았습니다. 비교 기준은 [시장조사 출처 기록](docs/MARKET_RESEARCH.md), 애착 인형과 성인 캐릭터 소비에 대한 기획 배경은 [프로젝트 기획서 1.4절·3절](https://drive.google.com/file/d/1AT0YGK2BfbWJpBcsvgHfugAlRHEdQTak/view)에 정리되어 있습니다.

### 5. 생산성 앱과 성인 키덜트 시장 사이에 자리 잡기

몽글마을은 **생산성 앱의 자기관리 수요**와 **성인 키덜트 시장의 캐릭터·애착 사물 소비**가 만나는 틈새를 겨냥했습니다. 포지셔닝의 두 축은 ‘자기관리 기능’과 ‘정서적 연결’이며, 두 요소를 함께 강화하는 것이 목표입니다.

![자기관리와 정서적 연결을 두 축으로 삼은 기획 당시 정성적 포지셔닝: 몽글마을은 두 요소가 모두 강한 영역을 목표로 함](docs/images/market-positioning.svg)

*발표 자료의 상대적 배치를 재구성한 기획 포지셔닝입니다. 좌표는 측정 점수가 아니며, 몽글마을의 위치는 달성한 성과가 아닌 제품이 지향하는 위치입니다.*

이를 제품에 옮긴 것이 **자연어 목표 → TODO·일정 관리 → 주민 퀘스트 → 완료 보상·주민 피드**입니다. 계획과 기록은 자기관리의 기반을 만들고, 나의 애착 인형으로 만든 주민과 그 주민의 활동 기록은 정서적 연결을 쌓도록 설계했습니다. 몽글마을은 이 둘을 결합해 **할 일을 끝내는 경험이, 내일도 다시 찾아올 이유로 이어지는 자기관리 서비스**를 만들고자 합니다. 실제 효과는 TODO 완료율, 1·7·30일 재방문율, 회고 참여율 등으로 검증할 과제입니다.

화면 구성은 [화면 설계서](https://drive.google.com/file/d/1YtJOZGWTRox2bAD4ejiBRfHChII9syMF/view), 사용 장면은 [시나리오 설계서](https://drive.google.com/file/d/1iEBtXu_PdO8v77O-_BnPvVMfbw2PgwJB/view), 기획과 현재 코드의 차이는 [설계·구현 대조 기록](docs/CROSS_REPOSITORY_REVIEW.md)에서 확인할 수 있습니다.

<details>
<summary>추가 리서치와 저장소별 설계 반영</summary>

기존 기획에서 참고한 시작의 부담과 루틴 앱 수요도 함께 반영했습니다. 아래 수치는 서로 다른 외부 조사에서 인용했으며, 출처 목록은 [프로젝트 기획서](https://drive.google.com/file/d/1AT0YGK2BfbWJpBcsvgHfugAlRHEdQTak/view)에서 확인할 수 있습니다.

| 관찰한 문제 | 조사 결과 | AI 설계에 반영한 방식 |
| --- | --- | --- |
| 시작 자체가 어렵다 | 귀찮음 **25.8%**, 무엇을 할지 모름 **24.4%**, 시간 부족 **21.7%** | 자연어 목표를 대화로 구체화하고 구조화된 TODO 후보 생성 |
| 생산성 앱을 오래 쓰기 어렵다 | 생산성 앱 리텐션: 1일 **32.86% → 30일 9.63%** | 애착 인형 기반 주민과 페르소나별 퀘스트·피드·답글 생성 |
| 루틴을 돕는 디지털 수요가 있다 | 챌린지·습관 앱 이용 **21.3%** | 사용자가 확인하고 저장할 수 있는 계획 초안 제공 |

</details>

## 사용자 흐름

```mermaid
flowchart TB
    JOIN["로그인 · 주민 입주"]
    PLAN["목표 구체화 · TODO 확정"]
    DO["퀘스트 연결<br/>완료 보상"]
    REVIEW["개인 피드 · 댓글 · 회고"]
    JOIN --> PLAN --> DO --> REVIEW
```

포모도로는 실행 중 독립적으로 사용하는 로컬 타이머입니다. 피드 생성 완료를 기다려야 포모도로·회고를 사용할 수 있는 순차 의존 관계는 없습니다. 아래 Server 경로의 공통 prefix는 `/api/v1`입니다.

| 단계 | Web 담당 | Server API·저장 | AI·경계 및 근거 |
| --- | --- | --- | --- |
| 로그인·세션 복구 | `auth/store.ts`, `auth/api.ts`, `shared/api/client.ts` | `POST /auth/login`, `/auth/token/refresh`; `GET /auth/me/`; Kakao 교환·가입 보완 | AI 미호출<br/>[src/features/auth/store.ts](https://github.com/bigmooon/mongle-web/blob/fcd2734b386035fca2d10980a1bb55ec8e90c4ba/src/features/auth/store.ts) · [apps/users/urls.py](https://github.com/bigmooon/mongle-server/blob/11f428734960dab8db60bc5bc7128fb62e8a495d/apps/users/urls.py) · [apps/users/refresh_token_service.py](https://github.com/bigmooon/mongle-server/blob/11f428734960dab8db60bc5bc7128fb62e8a495d/apps/users/refresh_token_service.py) |
| 사진·AI 주민 생성 | `character/api.ts`, `pendingJob.ts`, `App.tsx` | 원본 presign → S3 PUT → 생성 job 제출·조회 → `POST /characters/` 입주 | `/v1/character` → persona·이미지·외형 결과<br/>[src/features/character/api.ts](https://github.com/bigmooon/mongle-web/blob/fcd2734b386035fca2d10980a1bb55ec8e90c4ba/src/features/character/api.ts) · [apps/characters/views.py](https://github.com/bigmooon/mongle-server/blob/11f428734960dab8db60bc5bc7128fb62e8a495d/apps/characters/views.py) · [api/character_creation/router.py](https://github.com/bigmooon/mongle-ai/blob/8f897687560a6ebf179e3a0894a3bfd05b778efc/api/character_creation/router.py) |
| 자연어 목표·계획 구체화 | `todo/todoApi.ts`, `planner-chat/plannerApi.ts` | `/todos/generate/`, `/todos/chat/` 및 job 조회 | 단일 분해 또는 후속 질문·계획 후보. 생성만으로 DB에 저장하지 않음<br/>[src/features/planner-chat/plannerApi.ts](https://github.com/bigmooon/mongle-web/blob/fcd2734b386035fca2d10980a1bb55ec8e90c4ba/src/features/planner-chat/plannerApi.ts) · [apps/todos/ai_client.py](https://github.com/bigmooon/mongle-server/blob/11f428734960dab8db60bc5bc7128fb62e8a495d/apps/todos/ai_client.py) · [agents/todo_creation/planner/pipeline.py](https://github.com/bigmooon/mongle-ai/blob/8f897687560a6ebf179e3a0894a3bfd05b778efc/agents/todo_creation/planner/pipeline.py) |
| TODO·캘린더·태그 저장 | TODO 확정, 플래너 확정, `calendar/CalendarModal.tsx` | `/todos/confirm/`, `/todos/planner-confirm/`, `/todos/`, `/schedules/`, `/calendar/`, `/tags/` | 계획 확정은 Django가 오늘 후보를 Todo, 다른 날짜 후보를 Schedule로 저장; AI `/commit`은 이 제품 경로에서 호출하지 않음<br/>[apps/todos/views.py](https://github.com/bigmooon/mongle-server/blob/11f428734960dab8db60bc5bc7128fb62e8a495d/apps/todos/views.py) · [apps/todos/schedule_urls.py](https://github.com/bigmooon/mongle-server/blob/11f428734960dab8db60bc5bc7128fb62e8a495d/apps/todos/schedule_urls.py) · [src/features/calendar/CalendarModal.tsx](https://github.com/bigmooon/mongle-web/blob/fcd2734b386035fca2d10980a1bb55ec8e90c4ba/src/features/calendar/CalendarModal.tsx) |
| 캐릭터 퀘스트 배정 | `previewTodoQuests`, TODO·플래너 확정 UI | `/todos/quest-preview/` 또는 확정 중 `_assign_quests_to_todos` | `/v1/quest/generate`; TODO **ID**와 캐릭터 정보로 매핑. TODO 내용은 LLM에 전달하지 않음<br/>[apps/todos/views.py](https://github.com/bigmooon/mongle-server/blob/11f428734960dab8db60bc5bc7128fb62e8a495d/apps/todos/views.py) · [agents/quest_generation/pipeline.py](https://github.com/bigmooon/mongle-ai/blob/8f897687560a6ebf179e3a0894a3bfd05b778efc/agents/quest_generation/pipeline.py) |
| 완료·보상 | `completeTodo`, App/캘린더 상태 갱신 | `PATCH /todos/{id}/complete/` → Todo·Quest 완료, 잔액·거래 기록 → DB commit 후 피드 예약 | 피드 생성은 완료 응답과 분리<br/>[src/features/todo/todoApi.ts](https://github.com/bigmooon/mongle-web/blob/fcd2734b386035fca2d10980a1bb55ec8e90c4ba/src/features/todo/todoApi.ts) · [apps/todos/views.py](https://github.com/bigmooon/mongle-server/blob/11f428734960dab8db60bc5bc7128fb62e8a495d/apps/todos/views.py) |
| AI 이미지·캡션 | 생성된 피드·알림을 조회 | Celery `generate_feed_post` → AI 호출 → Post 저장·알림 생성 | `/v1/feed/generate`: 장면 프롬프트 → 이미지 → S3 → 캡션 → 결과<br/>[apps/posts/tasks.py](https://github.com/bigmooon/mongle-server/blob/11f428734960dab8db60bc5bc7128fb62e8a495d/apps/posts/tasks.py) · [agents/feed_generation/pipeline.py](https://github.com/bigmooon/mongle-ai/blob/8f897687560a6ebf179e3a0894a3bfd05b778efc/agents/feed_generation/pipeline.py) |
| 피드·댓글·답글 | `feed/api.ts`, `FeedModal.tsx`, `PostScreen.tsx` | `/posts/`, `/posts/{id}/comments/`, `/posts/{id}/like/`; 댓글 commit 후 600초 지연 예약 | `/v1/reply/generate` → Reply 저장. 자기 캐릭터의 개인 피드<br/>[src/features/feed/api.ts](https://github.com/bigmooon/mongle-web/blob/fcd2734b386035fca2d10980a1bb55ec8e90c4ba/src/features/feed/api.ts) · [apps/posts/views.py](https://github.com/bigmooon/mongle-server/blob/11f428734960dab8db60bc5bc7128fb62e8a495d/apps/posts/views.py) · [apps/posts/tasks.py](https://github.com/bigmooon/mongle-server/blob/11f428734960dab8db60bc5bc7128fb62e8a495d/apps/posts/tasks.py) |
| 포모도로 | `pomodoro/PomodoroHud.tsx`: 25분/5분, 종료 시 다음 모드에서 정지 | 서버 API·집중 이력 DB 저장 없음 | AI 미호출; `localStorage`의 종료 시각으로 복원<br/>[src/features/pomodoro/PomodoroHud.tsx](https://github.com/bigmooon/mongle-web/blob/fcd2734b386035fca2d10980a1bb55ec8e90c4ba/src/features/pomodoro/PomodoroHud.tsx) |
| 회고 | `reflection/api.ts`: 당일 문맥·과거 회고 조회, 작성·수정 | `/reflections/context/{date}/`, `/reflections/`, `/{id}/`; Reflection·보상 거래 저장 | AI 미호출<br/>[src/features/reflection/api.ts](https://github.com/bigmooon/mongle-web/blob/fcd2734b386035fca2d10980a1bb55ec8e90c4ba/src/features/reflection/api.ts) · [apps/todos/reflection_views.py](https://github.com/bigmooon/mongle-server/blob/11f428734960dab8db60bc5bc7128fb62e8a495d/apps/todos/reflection_views.py) |

### 에이전트·모델 추론과 구조화 출력

`api.main:app`이 기능 라우터를 등록하고 `api/deps.py`가 설정별 Ports를 주입합니다. 제품의 인증·사과 잔액·도메인 DB 저장은 Django 책임입니다. AI는 job·대화의 임시 메모리와 이미지 스토리지 I/O를 사용하므로, 외부 상태가 전혀 없는 순수 함수로 설명하지 않습니다.

| 기능 | 파이프라인·출력 | 실제 경계·근거 |
| --- | --- | --- |
| 캐릭터 | 입력 검증 → persona 및 원본 처리 → 이미지 생성 → 업로드 → 엔티티 조립 | [agents/character_creation/pipeline.py](https://github.com/bigmooon/mongle-ai/blob/8f897687560a6ebf179e3a0894a3bfd05b778efc/agents/character_creation/pipeline.py) · [api/deps.py](https://github.com/bigmooon/mongle-ai/blob/8f897687560a6ebf179e3a0894a3bfd05b778efc/api/deps.py). API 경로는 메모리 repository를 사용; 사용자 입주·Character DB 저장은 Django |
| 단일 TODO | 날짜·범위 분류, 명시된 할 일 분해, 후보 또는 범위 밖 응답 | [agents/todo_creation/todo/pipeline.py](https://github.com/bigmooon/mongle-ai/blob/8f897687560a6ebf179e3a0894a3bfd05b778efc/agents/todo_creation/todo/pipeline.py) · [api/deps.py](https://github.com/bigmooon/mongle-ai/blob/8f897687560a6ebf179e3a0894a3bfd05b778efc/api/deps.py). `base` 어댑터 사용; 후보는 확정 전까지 제품 DB에 미저장 |
| 플래너 | 충분성 판단 → 후속 질문/중단·재개 → 날짜별 계획 후보 | [agents/todo_creation/planner/graph.py](https://github.com/bigmooon/mongle-ai/blob/8f897687560a6ebf179e3a0894a3bfd05b778efc/agents/todo_creation/planner/graph.py) · [agents/todo_creation/planner/pipeline.py](https://github.com/bigmooon/mongle-ai/blob/8f897687560a6ebf179e3a0894a3bfd05b778efc/agents/todo_creation/planner/pipeline.py). `thread_id`와 `MemorySaver` 사용 |
| 퀘스트 | 캐릭터 풀 순환과 LLM runner → `generated`·`skipped` | [agents/quest_generation/pipeline.py](https://github.com/bigmooon/mongle-ai/blob/8f897687560a6ebf179e3a0894a3bfd05b778efc/agents/quest_generation/pipeline.py) · [agents/quest_generation/schemas.py](https://github.com/bigmooon/mongle-ai/blob/8f897687560a6ebf179e3a0894a3bfd05b778efc/agents/quest_generation/schemas.py). LangGraph가 아닌 순차 runner; TODO 내용은 입력에서 제외 |
| 피드 | 장면 프롬프트 → 이미지 생성 → S3 업로드 → 캡션 → 결과 | [agents/feed_generation/pipeline.py](https://github.com/bigmooon/mongle-ai/blob/8f897687560a6ebf179e3a0894a3bfd05b778efc/agents/feed_generation/pipeline.py) · [agents/feed_generation/nodes/gen_caption_prompt.py](https://github.com/bigmooon/mongle-ai/blob/8f897687560a6ebf179e3a0894a3bfd05b778efc/agents/feed_generation/nodes/gen_caption_prompt.py). 캡션은 장면 프롬프트·퀘스트·persona 사용; 생성 완료 이미지를 다시 VLM으로 판독하는 단계는 없음 |
| 답글 | 캐릭터·게시글 캡션·사용자 댓글 → 답글 | [agents/reply_generation/pipeline.py](https://github.com/bigmooon/mongle-ai/blob/8f897687560a6ebf179e3a0894a3bfd05b778efc/agents/reply_generation/pipeline.py) · [api/reply_generation/router.py](https://github.com/bigmooon/mongle-ai/blob/8f897687560a6ebf179e3a0894a3bfd05b778efc/api/reply_generation/router.py). 10분 예약과 Reply DB 저장은 Django Celery |

Pydantic 입력/출력 모델, 어댑터의 JSON 파싱·스키마 요청, 날짜·언어·길이 등 기능별 검증을 함께 사용합니다. 모든 경로가 동일한 모델이나 검증기를 사용하는 것은 아닙니다. 예를 들어 RunPod 플래너의 semantic validator는 `None`이며, `PLANNER_OPENAI_*`가 설정되면 플래너의 분류·후속 질문·검증·생성 경로를 별도 호환 API로 바꿉니다.

관련 코드: [api/deps.py](https://github.com/bigmooon/mongle-ai/blob/8f897687560a6ebf179e3a0894a3bfd05b778efc/api/deps.py) · [api/config.py](https://github.com/bigmooon/mongle-ai/blob/8f897687560a6ebf179e3a0894a3bfd05b778efc/api/config.py) · [adapters/todo_creation/qwen_llm.py](https://github.com/bigmooon/mongle-ai/blob/8f897687560a6ebf179e3a0894a3bfd05b778efc/adapters/todo_creation/qwen_llm.py) · [agents/todo_creation/schemas.py](https://github.com/bigmooon/mongle-ai/blob/8f897687560a6ebf179e3a0894a3bfd05b778efc/agents/todo_creation/schemas.py)

| 추론 구성 | 코드에서 확인한 선택지 |
| --- | --- |
| 텍스트 | `qwen` 호환 endpoint 또는 RunPod. 워커 기본 빌드는 Qwen2.5-7B, 플래너 이미지 빌드는 EXAONE-3.5-7.8B. 실제 배포 선택은 환경 변수·템플릿에 따름 |
| 이미지·시각 분석 | 통합 이미지 워커의 image_character·text_character·feed 모드. SDXL·ControlNet·LoRA는 이미지 합성, Qwen VL 계열은 외형 분석 등에 사용; VLM 자체를 이미지 생성 모델이라고 부르지 않음 |
| 로컬 검증 | 캐릭터 fake persona + mock 이미지 + local storage. TODO와 답글을 포함한 전체 제품 mock이 아님 |

관련 코드: [runpod_workers/llm/Dockerfile](https://github.com/bigmooon/mongle-ai/blob/8f897687560a6ebf179e3a0894a3bfd05b778efc/runpod_workers/llm/Dockerfile) · [.github/workflows/deploy-workers.yml](https://github.com/bigmooon/mongle-ai/blob/8f897687560a6ebf179e3a0894a3bfd05b778efc/.github/workflows/deploy-workers.yml) · [runpod_workers/image_gen/handler.py](https://github.com/bigmooon/mongle-ai/blob/8f897687560a6ebf179e3a0894a3bfd05b778efc/runpod_workers/image_gen/handler.py) · [runpod_workers/image_gen/model_refs.py](https://github.com/bigmooon/mongle-ai/blob/8f897687560a6ebf179e3a0894a3bfd05b778efc/runpod_workers/image_gen/model_refs.py) · [runpod_workers/image_gen/pipelines/image_character/mascot_stage.py](https://github.com/bigmooon/mongle-ai/blob/8f897687560a6ebf179e3a0894a3bfd05b778efc/runpod_workers/image_gen/pipelines/image_character/mascot_stage.py) · [api/deps.py](https://github.com/bigmooon/mongle-ai/blob/8f897687560a6ebf179e3a0894a3bfd05b778efc/api/deps.py)

### 메모리·재시도·복구 범위

캐릭터·TODO·플래너·퀘스트의 Submit/Poll은 `asyncio.create_task`와 프로세스 내 job store를 사용합니다. Celery·Redis는 이 AI API의 job backend가 아닙니다. 단일 Uvicorn 프로세스를 전제로 하며, 재시작 시 job과 플래너 체크포인트가 유실됩니다. 새로고침 복구는 Web의 캐릭터 pending 값과 Django DB 상태 조회가 담당하며, AI 프로세스 재시작 복구까지 보장하지 않습니다.

캐릭터 persona/source 업로드는 LangGraph RetryPolicy, 이미지·생성 업로드는 해당 노드의 재시도/정리 로직을 사용합니다. 피드는 이미지·S3·캡션의 특정 예외에 최대 3시도를 적용하고, 퀘스트는 실패 항목을 `skipped`로 반환합니다. 제품의 재처리·보상은 Django 정책과 함께 봐야 합니다.

관련 코드: [api/character_creation/jobs.py](https://github.com/bigmooon/mongle-ai/blob/8f897687560a6ebf179e3a0894a3bfd05b778efc/api/character_creation/jobs.py) · [api/todo_creation/jobs.py](https://github.com/bigmooon/mongle-ai/blob/8f897687560a6ebf179e3a0894a3bfd05b778efc/api/todo_creation/jobs.py) · [api/quest_generation/router.py](https://github.com/bigmooon/mongle-ai/blob/8f897687560a6ebf179e3a0894a3bfd05b778efc/api/quest_generation/router.py) · [agents/todo_creation/planner/graph.py](https://github.com/bigmooon/mongle-ai/blob/8f897687560a6ebf179e3a0894a3bfd05b778efc/agents/todo_creation/planner/graph.py) · [agents/character_creation/pipeline.py](https://github.com/bigmooon/mongle-ai/blob/8f897687560a6ebf179e3a0894a3bfd05b778efc/agents/character_creation/pipeline.py) · [agents/character_creation/nodes/image_generator.py](https://github.com/bigmooon/mongle-ai/blob/8f897687560a6ebf179e3a0894a3bfd05b778efc/agents/character_creation/nodes/image_generator.py) · [agents/character_creation/nodes/generated_upload.py](https://github.com/bigmooon/mongle-ai/blob/8f897687560a6ebf179e3a0894a3bfd05b778efc/agents/character_creation/nodes/generated_upload.py) · [agents/feed_generation/pipeline.py](https://github.com/bigmooon/mongle-ai/blob/8f897687560a6ebf179e3a0894a3bfd05b778efc/agents/feed_generation/pipeline.py) · [apps/characters/tasks.py](https://github.com/bigmooon/mongle-server/blob/11f428734960dab8db60bc5bc7128fb62e8a495d/apps/characters/tasks.py)

## 담당한 부분

이 저장소에서는 에이전트 설계부터 API·배포·평가까지 AI 기능의 전체 흐름을 구현했습니다. 아래 항목은 병합된 PR로 확인할 수 있습니다.

- **에이전트 구조**: 멀티턴 파이프라인과 상태 없는 엔진·어댑터 경계를 설계했습니다. ([#26](https://github.com/mong-studio/mongle-ai/pull/26), [#44](https://github.com/mong-studio/mongle-ai/pull/44))
- **서비스 API**: FastAPI 의존성 주입과 기능별 엔드포인트를 구성했습니다. ([#45](https://github.com/mong-studio/mongle-ai/pull/45), [#48](https://github.com/mong-studio/mongle-ai/pull/48))
- **학습·평가**: SFT 데이터셋, LoRA 학습 하네스, 언어 품질 게이트와 모델 벤치마크를 구축했습니다. ([#50](https://github.com/mong-studio/mongle-ai/pull/50), [#59](https://github.com/mong-studio/mongle-ai/pull/59), [#188](https://github.com/mong-studio/mongle-ai/pull/188))
- **비동기 처리**: 캐릭터와 TODO 생성 작업을 제출·조회 방식으로 전환했습니다. ([#100](https://github.com/mong-studio/mongle-ai/pull/100), [#103](https://github.com/mong-studio/mongle-ai/pull/103))
- **배포·운영**: RunPod 워커 배포, OIDC·SSM 기반 배포, 콜드 스타트와 메모리 사용을 개선했습니다. ([#72](https://github.com/mong-studio/mongle-ai/pull/72), [#82](https://github.com/mong-studio/mongle-ai/pull/82), [#121](https://github.com/mong-studio/mongle-ai/pull/121), [#167](https://github.com/mong-studio/mongle-ai/pull/167))
- **출력 안정성**: 날짜 추출, JSON 강제, 환각·압축 게이트와 회귀 평가를 추가했습니다. ([#109](https://github.com/mong-studio/mongle-ai/pull/109), [#135](https://github.com/mong-studio/mongle-ai/pull/135), [#150](https://github.com/mong-studio/mongle-ai/pull/150), [#190](https://github.com/mong-studio/mongle-ai/pull/190))

## 기술적 선택

| 문제 | 선택 | 이유 |
| --- | --- | --- |
| 여러 생성 단계를 안전하게 연결 | LangGraph + Pydantic 상태 모델 | 단계별 입력·출력을 검증하고 실패 지점을 분리하기 위해 |
| GPU 작업의 긴 응답 시간 | Submit/Poll 비동기 API | HTTP 타임아웃과 새로고침 이후 작업 유실을 줄이기 위해 |
| 모델·배포 환경 교체 | Protocol 기반 어댑터 | Qwen, RunPod, Fake provider를 도메인 로직과 분리하기 위해 |
| LLM의 형식 오류 | Schema 검증 + JSON 강제 + 후처리 게이트 | 자연어 품질과 API 계약을 함께 지키기 위해 |
| GPU 메모리 부족 | 멀티 LoRA·VAE tiling·콜드 스타트 최적화 | 제한된 추론 환경에서 여러 기능을 운영하기 위해 |

## 시스템 구조

AI는 Django가 전달한 입력을 구조화된 생성 결과로 반환하고, 설정된 추론·이미지 스토리지 어댑터를 실행합니다.

```mermaid
flowchart TB
    WEB["Web<br/>React · Phaser"]
    SERVER["Server<br/>Django · Celery"]
    AI["AI<br/>FastAPI · 추론"]
    DB["관계형 데이터<br/>MySQL"]
    MEDIA["이미지 객체<br/>S3"]

    WEB -->|제품 API| SERVER
    SERVER -->|내부 AI API| AI
    SERVER -->|도메인 저장| DB
    AI -->|생성 이미지 업로드| MEDIA
```

Web의 AI 기능 요청은 Django를 거쳐 FastAPI로 전달됩니다. 원본 사진은 Django가 발급한 presigned URL로 Web이 S3에 직접 PUT하며, Django는 이미지 키·메타데이터와 캐릭터 생성 감사 JSON을 관리합니다. AI가 결과를 HTTP 응답/폴링 결과로 반환하면 Django가 도메인 DB에 반영합니다. S3는 Web 정적 파일 배포와 사용자 미디어 저장에 각각 사용합니다.

Redis는 Server의 Celery broker/result 및 인증 캐시이고, AI job·플래너 대화는 별도 메모리 상태입니다. 제품 DB는 MySQL을 사용하도록 구성되어 있고, Django 기본 설정에서는 `DATABASE_URL`을 지정하지 않으면 SQLite를 사용합니다. [설정 근거](https://github.com/bigmooon/mongle-server/blob/11f428734960dab8db60bc5bc7128fb62e8a495d/config/settings/base.py).

관련 코드: [src/shared/api/client.ts](https://github.com/bigmooon/mongle-web/blob/fcd2734b386035fca2d10980a1bb55ec8e90c4ba/src/shared/api/client.ts) · [src/features/character/api.ts](https://github.com/bigmooon/mongle-web/blob/fcd2734b386035fca2d10980a1bb55ec8e90c4ba/src/features/character/api.ts) · [apps/characters/tasks.py](https://github.com/bigmooon/mongle-server/blob/11f428734960dab8db60bc5bc7128fb62e8a495d/apps/characters/tasks.py) · [infrastructure/storage/s3.py](https://github.com/bigmooon/mongle-server/blob/11f428734960dab8db60bc5bc7128fb62e8a495d/infrastructure/storage/s3.py) · [api/deps.py](https://github.com/bigmooon/mongle-ai/blob/8f897687560a6ebf179e3a0894a3bfd05b778efc/api/deps.py)

### 작업별 통신 방식

| 작업 | Web → Django | Django → AI | 실행·상태 책임 |
| --- | --- | --- | --- |
| 캐릭터 | `POST /characters/generation-jobs/` → 202; `GET /characters/generation-jobs/{id}/` | Celery가 `POST /v1/character` → 202 후 `GET /v1/character/{id}` 폴링 | Django `CharacterGenerationJob` DB 상태 + AI 메모리 job. 성공 후 사용자의 `POST /characters/`로 입주 |
| 단일 TODO 후보 | `POST /todos/generate/`의 최종 응답 대기 | Django 요청 안에서 `POST /v1/todo/generate` 및 `GET /v1/todo/generate/{id}` | Celery 없음. Web에 job ID를 노출하는 방식이 아님 |
| 멀티턴 플래너 | `POST /todos/chat/` → 202; `GET /todos/chat/{id}/` 폴링 | Django가 `/v1/todo/chat` 제출·조회 중계 | AI 메모리 job·플래너 체크포인트. Django DB job 없음 |
| 퀘스트 | 미리보기·확정 API의 최종 응답 대기 | Django 요청 안에서 `/v1/quest/generate` 제출·조회 | Celery 없음. 결과의 유효한 매핑을 Django가 저장 |
| 피드·답글 | TODO 완료·댓글 등록 후 게시물 재조회 | Celery가 `POST /v1/feed/generate`, `/v1/reply/generate` 결과 대기 | Web 관점 백그라운드, AI API 관점 단일 요청/응답. 별도 feed job 조회 API 없음 |

Web → Django 경로에는 `/api/v1`을 앞에 붙입니다. 캐릭터의 Server job ID와 AI job ID는 서로 다르며, 플래너는 AI job ID를 중계합니다. **Submit/Poll이 곧 Celery 사용이나 영속 복구를 뜻하지는 않습니다.**

관련 코드: [apps/todos/views.py](https://github.com/bigmooon/mongle-server/blob/11f428734960dab8db60bc5bc7128fb62e8a495d/apps/todos/views.py) · [apps/todos/ai_client.py](https://github.com/bigmooon/mongle-server/blob/11f428734960dab8db60bc5bc7128fb62e8a495d/apps/todos/ai_client.py) · [apps/characters/tasks.py](https://github.com/bigmooon/mongle-server/blob/11f428734960dab8db60bc5bc7128fb62e8a495d/apps/characters/tasks.py) · [apps/posts/tasks.py](https://github.com/bigmooon/mongle-server/blob/11f428734960dab8db60bc5bc7128fb62e8a495d/apps/posts/tasks.py) · [api/todo_creation/router.py](https://github.com/bigmooon/mongle-ai/blob/8f897687560a6ebf179e3a0894a3bfd05b778efc/api/todo_creation/router.py) · [api/quest_generation/router.py](https://github.com/bigmooon/mongle-ai/blob/8f897687560a6ebf179e3a0894a3bfd05b778efc/api/quest_generation/router.py)


## 문서 기준과 변경 이력

README는 2026-10-10에 확인한 코드와 환경 변수 예시, Compose, CI 설정을 기준으로 작성했습니다. 코드 링크는 당시 커밋을 가리킵니다. Drive 설계 자료와 달라진 부분, 확인이 필요한 항목과 검증 내역은 [교차검증 기록](docs/CROSS_REPOSITORY_REVIEW.md)에서 확인할 수 있습니다.

## 관련 설계 문서

| 문서 | 확인할 수 있는 내용 |
| --- | --- |
| [프로젝트 기획서](https://drive.google.com/file/d/1AT0YGK2BfbWJpBcsvgHfugAlRHEdQTak/view) | 대상 사용자, 문제 정의와 제품 가설 |
| [시스템 아키텍처](https://drive.google.com/file/d/15p49ZUIrJCmrSCy3LpU3FbjapZaMXdRc/view) | Web·Server·AI 간 구성과 배포 경계 |
| [모델 테스트 계획 및 결과](https://drive.google.com/file/d/1tozTGjdvfpLf77Z2kIV1dezihjXp5j8Q/view) | 후보 모델 비교 기준과 평가 결과 |
| [인공지능 학습 결과](https://drive.google.com/file/d/1HbuCap2QbnE1OPwZdbhJJ3A1_DMbDImX/view) | 학습 과정과 실험 결과 |
| [AI 데이터 전처리 결과](https://drive.google.com/file/d/1Pxsk397u0joC_Bp-wbrbsc3p86MU6oar/view) | 데이터 정제·가공 과정 |

[전체 프로젝트 산출물 보기](https://drive.google.com/drive/folders/1Lfv49TDbilo4ivoSIpw4v8RDEnEw9quC)

## 평가 결과

아래 수치는 **프로젝트 제출 당시 평가 환경**의 결과입니다. 이후 모델과 파이프라인이 변경되었으므로 현재 운영 성능으로 일반화하지 않습니다.

| 평가 항목 | 결과 |
| --- | ---: |
| 7개 LLM 후보 중 Qwen2.5-7B 종합점수 | 3.672 / 5 |
| JSON / Schema 준수율 | 0.90 / 0.90 |
| 한국어 출력 비율 | 1.00 |
| 캐릭터 이미지 SSIM | 0.6712 → 0.8378 |
| VLM 객체·색상 인식 | 20/20 · 20/20 |
| 피드 이미지 생성 성공 | 19/20 |

평가 조건: LLM 표의 3.672는 7개 후보·5개 기능·총 50개 샘플 기준의 기존 Final 평균이며, 자동 점수 0.45 + GPT-5.5 judge 점수 0.55의 결합입니다. 속도나 현행 EXAONE/LoRA 성능을 나타내는 수치가 아닙니다. SSIM·VLM·피드 수치는 각각 별도의 평가 과제에서 얻은 결과이며, 50개 LLM 표본과는 평가 대상이 다릅니다. [LLM 평가 조건](llm_evaluation/llm-model-cost-summary.md), [제출 당시 모델 평가](https://drive.google.com/file/d/1tozTGjdvfpLf77Z2kIV1dezihjXp5j8Q/view), [학습 결과](https://drive.google.com/file/d/1HbuCap2QbnE1OPwZdbhJJ3A1_DMbDImX/view).

CI workflow는 외부 모델이 필요한 contract 테스트를 제외하고 `agents`, `adapters`, `api` 테스트와 80% 커버리지 게이트를 실행하도록 구성되어 있습니다.

## 빠른 시작

### 요구 환경

- Python 3.11+
- [uv](https://docs.astral.sh/uv/)

```bash
git clone https://github.com/bigmooon/mongle-ai.git
cd mongle-ai
cp .env.example .env
uv sync --group dev
```

GPU나 외부 모델 없이 **캐릭터 API 경계**를 확인하려면 `.env`를 다음처럼 설정합니다. TODO·답글에는 별도 모델 설정이 필요하며, `IMAGE_PROVIDER=mock`은 피드 이미지 전체를 대체하지 않습니다. (근거: [`api/deps.py`](api/deps.py), [로컬 캐릭터 검증](docs/local-character-mock.md))

```dotenv
LLM_PROVIDER=fake
QUEST_LLM_PROVIDER=fake
FEED_LLM_PROVIDER=fake
IMAGE_PROVIDER=mock
STORAGE_BACKEND=local
STORAGE=local
MONGLE_API_KEY=local-secret
```

```bash
uv run uvicorn api.main:app --reload --port 8010
```

API 문서는 `http://127.0.0.1:8010/docs`에서 확인할 수 있습니다.

### 검증

```bash
uv run pytest
```

외부 Qwen·RunPod가 필요한 contract 테스트는 기본 테스트에서 제외됩니다.

## 주요 API

| 기능 | 방식 | 경로 |
| --- | --- | --- |
| TODO 생성 | 비동기 Submit/Poll | `POST /v1/todo/generate`, `GET /v1/todo/generate/{job_id}` |
| 멀티턴 플래너 | 비동기 Submit/Poll | `POST /v1/todo/chat`, `GET /v1/todo/chat/{job_id}` |
| 캐릭터 생성 | 비동기 Submit/Poll | `POST /v1/character`, `GET /v1/character/{job_id}` |
| 퀘스트 분배 | 비동기 Submit/Poll | `POST /v1/quest/generate`, `GET /v1/quest/generate/{job_id}` |
| 메모리 commit | 동기 처리·제품 DB 저장 아님 | `POST /v1/todo/commit` |
| 캐릭터 예열 | best-effort 백그라운드 | `POST /v1/character/warmup` |
| 피드·답글 | 단일 요청/응답 | `POST /v1/feed/generate`, `POST /v1/reply/generate` |

## 디렉터리 구조

```text
agents/          기능별 오케스트레이션과 도메인 규칙
adapters/        LLM·RunPod·S3·메모리 구현체
api/             FastAPI 라우터와 비동기 작업 경계
runpod_workers/  LLM·이미지 생성 워커
sft_pipeline/    데이터 준비와 파인튜닝 실험
llm_evaluation/ 모델 비교와 회귀 평가
tests/           단위·통합 테스트
docs/            제품·데이터·기능별 설계 문서
```

## 배포

| 서비스 | 저장소에 정의된 배포·통신 경로 |
| --- | --- |
| Web | Node 빌드 → S3 정적 배포 → CloudFront invalidation. 개발은 Vite `/api` proxy → `localhost:8000`; 배포는 빌드 시 `VITE_API_BASE` 주입 |
| Server | 테스트 → Docker Hub → AWS OIDC·SSM → EC2 Compose. Nginx TLS → `web:8000` Gunicorn → Django. DB 주소는 `DATABASE_URL`, AI 주소는 아래 두 설정군 사용 |
| AI API | 테스트 → Docker Hub → RunPod CPU Pod 재시작 → `8010/health` 확인. Compose의 단독 API 실행과 GPU 워커는 별도 구성 |
| 추론 워커 | LLM·플래너·이미지 Docker 이미지 빌드. `v*` 태그 workflow에서 RunPod 템플릿 갱신. FastAPI가 RunPod endpoint를 호출하고 결과를 수집 |

Server의 TODO·퀘스트는 `MONGLE_AI_API_BASE`/`MONGLE_AI_API_KEY`, 캐릭터·피드·답글은 `AI_SERVICE_URL`/`AI_SERVICE_TOKEN`을 사용합니다. 두 키는 연결할 AI의 `MONGLE_API_KEY`와 맞춰야 합니다. 컨테이너에서 호스트 AI에 연결할 때 loopback 대신 도달 가능한 호스트 주소를 설정해야 합니다.

배포 경로는 저장소의 Compose와 CI 설정을 기준으로 정리했습니다. 실제 DNS, CloudFront origin, RDS 엔진 버전, RunPod에서 사용 중인 모델과 비밀 환경 변수는 운영 환경에서 별도로 확인해야 합니다. Nginx 대기 제한(120초), Server AI 폴링 기본 예산(150초), Gunicorn 제한(180초)이 달라 동기 대기 경로의 타임아웃 위험도 남아 있습니다.

관련 코드: [.github/workflows/deploy-web.yml](https://github.com/bigmooon/mongle-web/blob/fcd2734b386035fca2d10980a1bb55ec8e90c4ba/.github/workflows/deploy-web.yml) · [vite.config.ts](https://github.com/bigmooon/mongle-web/blob/fcd2734b386035fca2d10980a1bb55ec8e90c4ba/vite.config.ts) · [.github/workflows/deploy-server.yml](https://github.com/bigmooon/mongle-server/blob/11f428734960dab8db60bc5bc7128fb62e8a495d/.github/workflows/deploy-server.yml) · [nginx/api.conf](https://github.com/bigmooon/mongle-server/blob/11f428734960dab8db60bc5bc7128fb62e8a495d/nginx/api.conf) · [Dockerfile](https://github.com/bigmooon/mongle-server/blob/11f428734960dab8db60bc5bc7128fb62e8a495d/Dockerfile) · [.env.example](https://github.com/bigmooon/mongle-server/blob/11f428734960dab8db60bc5bc7128fb62e8a495d/.env.example) · [.github/workflows/deploy-api.yml](https://github.com/bigmooon/mongle-ai/blob/8f897687560a6ebf179e3a0894a3bfd05b778efc/.github/workflows/deploy-api.yml) · [.github/workflows/deploy-workers.yml](https://github.com/bigmooon/mongle-ai/blob/8f897687560a6ebf179e3a0894a3bfd05b778efc/.github/workflows/deploy-workers.yml) · [docker-compose.yml](https://github.com/bigmooon/mongle-ai/blob/8f897687560a6ebf179e3a0894a3bfd05b778efc/docker-compose.yml)

## 한계와 다음 과제

- 외부 GPU와 모델 엔드포인트가 필요한 전체 E2E는 로컬 기본 테스트에 포함되지 않습니다.
- 제출 당시 평가 결과와 현재 런타임 모델의 성능을 같은 기준으로 다시 측정할 필요가 있습니다.
- 이미지 생성과 장기 플래너의 지연 시간을 사용자 환경 기준으로 지속 측정해야 합니다.

## 팀

| 이름 | GitHub |
| --- | --- |
| 임정희 | [@bigmooon](https://github.com/bigmooon) |
| 박영훈 | [@aprkaos56](https://github.com/aprkaos56) |
| 정석원 | [@JeongSW123](https://github.com/JeongSW123) |
| 조아름 | [@areum117](https://github.com/areum117) |
| 최하진 | [@hun6684](https://github.com/hun6684) |
