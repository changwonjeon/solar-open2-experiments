# 06-practice-aaws — Solar Open 2 API 에이전트 평가 실습

## 실습 개요

2026년 7월 28일 LGCNS 사내교육 Day 2 미션으로, LangGraph/LangChain 기반 AAWS 에서 **Solar Open 2(`solar-open2`)** 를 모델의 두뇌로 연결했을 때 Supervisor, Navigator, Coder, Analyst 역할별 수행 능력을 공정하고 반복 가능하게 평가하는 실습 작업 공간입니다.

> 평가 대상은 Claude Code 사용 능력이 아니라, LangChain 에이전트의 모델로 연결된 Solar Open 2 의 역할별 성공률·정확성·비용·지연·복구력입니다.

## 상태

🟡 **실습 진행 중** — 사전 준비(Step 0) 완료, Mission 1 실행 중

### 진행 상황 (2026-07-28 기준)

| 항목 | 상태 | 비고 |
|------|------|------|
| AAWS 클론 및 환경 구성 | ✅ 완료 | `tasks/06-practice-aaws/aaws/` 에 git submodule 로 추가 |
| `.env` 파일 세팅 (`UPSTAGE_API_KEY` 등) | ✅ 완료 | `aaws/.env` 로 복사 완료 |
| `docs/` / `data/` / `output/` 디렉토리 구성 | ✅ 완료 | OKF 계층 구조 준비 완료 |
| Step 0-1. 환경 구성 | ✅ 완료 | `.env` 에 API 키 세팅 완료 |
| Step 0-2. 단독 API 호출 확인 (`test_upstage.py`) | ⏳ 진행 중 | `uv run python test_upstage.py` 실행 및 검증 |
| Mission 1. 역할별 웹 수집 에이전트 평가 | ⏳ 진행 중 | `test_config.yaml` 시나리오 활성화 후 파일럿 실행 |
| Mission 2. Solar Analyst 에이전트 구축·평가 | ⏳ 대기 중 | Mission 1 완료 후 진행 |
| Mission 3. Solar 에이전트 고도화 (Memory/Fallback/Skills) | ⏳ 대기 중 | Mission 1·2 baseline 동결 후 진행 |

## 계층 구조

```
tasks/06-practice-aaws/
├── aaws/                      # ← git submodule (AAWS 원본, 실습 중 수정 허용)
│   ├── app/                   # 에이전트 시스템 (Navigator/Coder/Supervisor/Analyst)
│   │   ├── agents/            # 에이전트 구현
│   │   ├── tools/             # 에이전트 도구 모음
│   │   ├── prompts/           # 시스템 프롬프트
│   │   └── schemas.py         # Pydantic 스키마
│   ├── notebooks/             # 1~5 일차 Jupyter 노트북 (참조용)
│   ├── artifacts/             # 시나리오 명세 및 수집 결과
│   │   ├── scenarios/         # 9 개 난이도별 시나리오 (.md)
│   │   └── results/           # 평가 리포트 및 크롤링 결과 JSON
│   ├── tests/                 # 평가 러너
│   │   ├── run_sequential_scenarios.py
│   │   ├── run_supervisor_scenarios.py
│   │   └── test_config.yaml   # 시나리오 선택 config
│   ├── install/               # 설치 스크립트
│   ├── Mission.md             # 기존 Day 2 미션 (참조용)
│   ├── Mission_upstage.md     # 실제 실행 미션 (Solar Open 2 API 평가)
│   ├── test_upstage.py        # Solar Open 2 단독 API 연결 검증 스크립트
│   └── .env                   # API 키 (gitignore 필수)
├── docs/                      # OKF Wiki 문서 (experiment-log, 분석 리포트)
├── data/                      # 실험 데이터 (시나리오 결과, 고정 fixture, gold dataset)
├── output/                    # 생성 산출물 (LLMs-as-a-Judge 평가 리포트, 차트, 보고서)
├── AGENTS.md                  # 태스크 로컬 규칙
├── CLAUDE.md                  # 태스크 로컬 지시
└── README.md                  # 이 파일
```

## Canonical Source

- AAWS 원본: `aaws/` (git submodule)
- 실제 실행 미션: `aaws/Mission_upstage.md`
- 참고 미션: `aaws/Mission.md` (기존 Day 2 미션, 참조용)

## 진입점

| 목적 | 경로 |
|------|------|
| Solar API 연결 검증 | `aaws/test_upstage.py` |
| Supervisor 시나리오 실행 | `aaws/tests/run_supervisor_scenarios.py` |
| Sequential 시나리오 실행 | `aaws/tests/run_sequential_scenarios.py` |
| 시나리오 선택 | `aaws/tests/test_config.yaml` |
| 실습 미션 가이드 | `aaws/Mission_upstage.md` |
| OKF 위키 | `docs/` |

## Mission 구조 (Mission_upstage.md 기준)

### Mission 1 — 역할별 웹 수집 에이전트 평가 (🟢 핵심)
Solar Open 2 가 어떤 역할에 적합한지 분리해 평가. 동일 프롬프트·도구·시나리오에서 모델 조건만 변경해 비교:

| 조건 | Supervisor | Navigator | Coder | 평가 목적 |
|---|---|---|---|---|
| `GGG` | Gemini | Gemini | Gemini | 기준선 |
| `SSS` | Solar | Solar | Solar | Solar 전체 팀 |
| `SGG` | Solar | Gemini | Gemini | Solar 의 위임·조정 능력 |
| `GSG` | Gemini | Solar | Gemini | Solar 의 탐색·Blueprint 능력 |
| `GGS` | Gemini | Gemini | Solar | Solar 의 코드 생성·실행·복구 능력 |

**평가 시나리오 (권장):**
- Level 1: `quotes_01_pagination.md`, `quotes_02_tag_filter.md`
- Level 2: `ajax_01_playwright_wait.md`, `ajax_02_api_reverse_engineering.md`

### Mission 2 — Solar Analyst 에이전트 구축·평가 (🟡)
Mission 1 에서 수집한 JSON 을 분석·시각화하는 Analyst 에이전트 추가. Solar 의 데이터 해석 능력을 별도 평가.

### Mission 3 — Solar 에이전트 고도화 (🔴 선택)
- **Track A**: Pattern Memory (성공·실패 패턴 기록 및 주입)
- **Track B**: Model Fallback (Solar → Gemini / Gemini → Solar 전환 복구)
- **Track C**: Skill System (도메인별 Skill 동적 제공)
- **Track D**: 사용자 정의 시나리오 (검증 가능한 신규 시나리오)

## 주요 산출물 (실습 진행에 따라 생성 예정)

- [`docs/experiment-log.md`](docs/experiment-log.md) — 실습 진행 일지 (일일 기록)
- [`docs/analysis-report.md`](docs/analysis-report.md) — 멀티에이전트 성능 분석 리포트 (Mission 1 완료 후 작성)
- [`docs/final-evaluation-report.md`](docs/final-evaluation-report.md) — 최종 결과 보고서 (Mission 1~3 완료 후 작성)
- `output/scenario-sequential-results/` — Sequential 파이프라인 평가 결과
- `output/scenario-supervisor-results/` — Supervisor 파이프라인 평가 결과
- `data/fixtures/` — 고정 HTML/API fixture (라이브 환경 평가 분리용)
- `data/gold/` — gold dataset (결정론적 정확도 채점용)

## 평가 지표

### 필수 지표
| 지표 | 의미 |
|---|---|
| Schema pass | JSON 구조와 타입 준수 |
| Task completion | 요구한 결과 파일 생성과 정상 종료 |
| Record completeness | 필수 레코드 수 대비 수집률 |
| Value accuracy | gold 값과 정확히 일치한 필드 비율 |
| Missing rate | 필수 필드 누락률 |
| Duplicate rate | 중복 레코드 비율 |
| Filter compliance | 요청 조건을 만족한 레코드 비율 |
| Page coverage | 요구 페이지 또는 상세 URL 방문 비율 |

### 권장 종합 가중치
| 평가 영역 | 비중 |
|---|---|
| 내용 정확성·완전성 | 40% |
| 작업 완료 | 20% |
| 형식 정확성 | 20% |
| 전략 효율 | 10% |
| 비용·지연·재시도 | 10% |

### 실패 유형 분류
| 실패 유형 | 예시 |
|---|---|
| `instruction` | 목표, 필터 또는 저장 경로 오해 |
| `orchestration` | Supervisor 가 역할을 잘못 위임하거나 완료를 조기 선언 |
| `navigation` | 잘못된 URL·selector·렌더링 전략 |
| `structured_output` | Blueprint 또는 JSON 형식 생성 실패 |
| `coding` | 문법, import, 런타임 오류 |
| `recovery` | 오류 원인을 찾지 못하거나 같은 실패 반복 |
| `persistence` | 결과 파일 누락 또는 잘못된 경로 저장 |
| `content` | 스키마는 맞지만 값이 틀리거나 누락됨 |
| `site_environment` | 사이트 변경, 차단, 네트워크 장애 |
| `model_api` | 인증, timeout, rate limit, 공급자 오류 |
| `evaluator` | Judge 파싱 또는 채점 실패 |

> `site_environment`, `model_api`, `evaluator` 오류는 에이전트 능력 실패와 분리해 집계합니다.

## 실전 명령어

```bash
cd tasks/06-practice-aaws/aaws

# 1. Solar API 단독 연결 확인
uv run python test_upstage.py

# 2. 시나리오 선택 (tests/test_config.yaml 에서 주석 해제)
vim tests/test_config.yaml

# 3. Gemini 전체 팀
uv run python -m tests.run_supervisor_scenarios --model-mode gemini

# 4. Solar 전체 팀
uv run python -m tests.run_supervisor_scenarios --model-mode upstage

# 5. Gemini와 Solar 전체 팀 순차 실행
uv run python -m tests.run_supervisor_scenarios --model-mode both

# 6. Sequential 파이프라인
uv run python -m tests.run_sequential_scenarios
```

## 실습 수정 가이드

- `aaws/` 내 파일 수정 시: 실습 중 자유롭게 수정 가능 (Source 불변성 예외)
- `docs/` 내 문서 작성 시: OKF frontmatter(`type`, `timestamp`, `tags`) 준수
- `output/` 내 산출물: solar-open2 실행 결과만 저장, 중간 작업 파일은 `data/` 에 보관
- `git add`/`commit`/`push`: 사용자 승인 후에만 실행

---

## 하위 태스크

| ID | 미션 | 내용 | 상태 |
|---|---|---|---|
| 06-01 | 사전 준비 | API 키 세팅, `test_upstage.py` 검증, LangSmith trace 확인 | ✅ 완료 |
| 06-02 | Mission 1-1 | Level 1 시나리오 파일럿 (`GGG`, `SSS`) | ⏳ 진행 중 |
| 06-03 | Mission 1-2 | 역할별 교차 비교 (`SGG`, `GSG`, `GGS`) 파일럿 | ⏳ 대기 중 |
| 06-04 | Mission 1-3 | 유효 조건별 5 회 본 실험 + 결정론적 채점 | ⏳ 대기 중 |
| 06-05 | Mission 2 | Analyst 에이전트 구축 및 Solar 평가 | ⏳ 대기 중 |
| 06-06 | Mission 3 | Memory/Fallback/Skills 고도화 실험 | ⏳ 대기 중 |
| 06-07 | 최종 보고 | 역할별 결론, 실패 분석, 운영 판단 문서화 | ⏳ 대기 중 |

생성 후 다음 명령으로 전체 파일 목록을 확인하십시오:

```bash
find tasks/06-practice-aaws/ -type f | sort
```
