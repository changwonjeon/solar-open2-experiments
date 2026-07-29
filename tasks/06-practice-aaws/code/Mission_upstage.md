# 🎯 Day 2 Mission — AAWS 기본 미션 + Solar Open 2 A/B

> **목표:** 기존 AAWS Mission을 Gemini로 완성하고, 중요한 텍스트 역할과
> 노드에 Upstage `solar-open2`를 선택적으로 투입해 성능과 운영 특성을
> 비교합니다.

이 미션은 Claude Code 사용 능력을 평가하지 않습니다. 기본 산출물의
완성과 학습 목표는 원본 `Mission.md`를 따릅니다. 추가 평가 대상은
LangChain 에이전트의 모델 또는 텍스트 노드로 연결된 Solar Open 2이며,
Gemini 기준선과 비교해 성공·정확성·비용·지연·복구력을 관찰합니다.

기존 [`Mission.md`](Mission.md)를 기본 미션으로 유지합니다. 원래의 점진적
학습 흐름과 Gemini 기반 기능을 빠뜨리지 않고 수행하면서, 텍스트 작업에는
Solar Open 2 조건을 부가해 역할별 성능을 관찰합니다. Mission 2·3의 기본
실행 주체는 전체 기능을 수행하는 Gemini이며, 그중 중요한 텍스트 단계만
Solar Open 2로 교체하는 작은 A/B 실험을 추가합니다.

## 🧩 모델별 기능 범위

원본 `Mission.md`의 기능을 모델 간 공통 분모로 축소하지 않습니다.
멀티모달 기능은 Gemini로 그대로 구현하고, `solar-open2`는 지원되는 텍스트
기능에 추가해 비교합니다.

| 기능 | Gemini | Solar Open 2 | 비교 원칙 |
|---|---|---|---|
| 텍스트 지시·분석·코드·도구 호출 | 사용 | 사용 | 같은 입력과 도구로 비교 가능 |
| DOM/HTML/API 기반 웹 탐색 | 사용 | 사용 | 텍스트 기반 역할 비교 가능 |
| 이미지 생성·편집 | 사용 | 사용하지 않음 | Gemini 전용 기능으로 기록 |
| 이미지·스크린샷·PDF Vision, OCR | 사용 | 사용하지 않음 | Gemini 전용 기능으로 기록 |
| 코드 기반 차트 렌더링 | 사용 | 사용 | 모델은 코드를 작성하고 Python이 렌더링 |

Nano Banana 인포그래픽이나 Vision 분석처럼 Gemini가 맡은 멀티모달 단계는
Gemini 기본 파이프라인에서 그대로 수행합니다. Mission 2·3의 B 조건도
멀티모달 단계는 Gemini로 고정하고, 선택한 텍스트 노드만 Solar Open 2로
교체합니다. 따라서 A/B 차이는 교체한 텍스트 노드의 입력·출력에서
평가하고, 전체 파이프라인 성공을 Solar 단독 성공이라고 부르지 않습니다.

## 📖 모델 조건 표기법

실험 조건의 세 글자는 앞에서부터 각 에이전트 역할에 사용할 모델을
나타냅니다.

```text
첫째 자리: Supervisor
둘째 자리: Navigator
셋째 자리: Coder

G: Gemini
S: Solar Open 2
```

예를 들어 `SGG`는 Supervisor만 Solar Open 2를 사용하고 Navigator와
Coder는 Gemini를 사용하는 조건입니다.

| 조건 | Supervisor | Navigator | Coder | 의미 |
|---|---|---|---|---|
| `GGG` | Gemini | Gemini | Gemini | 모든 역할에 Gemini를 사용하는 기준선 |
| `SSS` | Solar Open 2 | Solar Open 2 | Solar Open 2 | 모든 역할에 Solar Open 2 사용 |
| `SGG` | Solar Open 2 | Gemini | Gemini | Solar의 Supervisor 역할 평가 |
| `GSG` | Gemini | Solar Open 2 | Gemini | Solar의 Navigator 역할 평가 |
| `GGS` | Gemini | Gemini | Solar Open 2 | Solar의 Coder 역할 평가 |

---

## 📋 전체 미션 개요

| 미션 | 주제 | 핵심 질문 |
|:---:|---|---|
| **Mission 1** | 역할별 기준선과 프롬프트 튜닝 | 역할별 실패를 프롬프트 수정만으로 개선할 수 있는가? |
| **Mission 2** | Analyst 에이전트 구축·평가 | 원래 분석·시각화 파이프라인에 Solar 텍스트 비교를 추가할 수 있는가? |
| **Mission 3** | 에이전트 고도화 | Memory, Fallback, Skills가 Solar 성능에 어떤 영향을 주는가? |

## 평가 원칙

1. **같은 조건으로 비교합니다.** 모델 외의 프롬프트, 도구, temperature,
   시나리오, 최대 재시도와 실행 환경을 동일하게 유지합니다.
2. **한 번의 성공으로 일반화하지 않습니다.** Mission 1의 첫 기준선은
   튜닝 대상을 찾는 탐색 실험으로만 해석합니다. 반복은 전후 차이가
   불명확할 때 선택적으로 추가하며, 표본 수를 결과에 명시합니다.
3. **형식과 내용을 분리해 채점합니다.** JSON Schema 통과와 실제 수집값의
   정확성은 다른 지표입니다.
4. **모델 실패와 환경 실패를 분리합니다.** 네트워크, 사이트 변경, 차단,
   API rate limit은 별도 오류로 기록합니다.
5. **Fallback 성공을 Solar 단독 성공으로 계산하지 않습니다.**
6. **실패한 실행도 보존합니다.** 로그와 partial output을 삭제하지 않습니다.

---

## 🧪 사전 준비 — Solar Open 2 API 연결 확인

### Step 0-1. 환경 구성

`.env_template`을 참고해 로컬 `.env`에 필요한 키를 설정합니다. 실제 키는
Git에 추가하지 않습니다.

```env
UPSTAGE_API_KEY="your-api-key"
GOOGLE_API_KEY="your-api-key"
TAVILY_API_KEY="your-api-key"

LANGSMITH_API_KEY="your-langsmith-key"
LANGSMITH_TRACING=true
LANGCHAIN_TRACING_V2=true

AAWS_LANGSMITH_PROJECT_GEMINI="aaws-supervisor-gemini"
AAWS_LANGSMITH_PROJECT_UPSTAGE="aaws-supervisor-solar-open2"
```

필요한 Upstage 통합 패키지는 `install/requirements.txt`의
`langchain-upstage`입니다.

#### 로컬 `.venv` 사용 시 유의점

이 저장소는 상위 프로젝트에도 `.venv`가 있을 수 있습니다. 이 상태에서
단순히 `uv run ...`을 실행하면 저장소의 `./.venv` 대신 상위 프로젝트의
가상환경을 선택할 수 있습니다. 실제로 상위 환경이 선택되면
`ModuleNotFoundError: No module named 'langchain_upstage'`처럼 로컬
환경에는 설치된 패키지를 찾지 못할 수 있습니다.

실험 전 다음 명령으로 현재 인터프리터와 핵심 패키지를 확인합니다.

```bash
./.venv/bin/python -c \
  "import sys, importlib.metadata; print(sys.executable); print(importlib.metadata.version('langchain-upstage'))"
```

가장 재현 가능한 실행 방법은 저장소의 Python을 직접 지정하는 것입니다.

```bash
./.venv/bin/python test_upstage.py
./.venv/bin/python -m tests.run_supervisor_scenarios --model-mode both
./.venv/bin/python -m tests.run_sequential_scenarios
```

이미 `./.venv`가 활성화된 셸에서 `uv`를 사용한다면 `uv run --active`로
활성 환경을 명시합니다.

```bash
uv run --active python test_upstage.py
```

명령 실행 시 표시되는 인터프리터 경로가 이 저장소의 `./.venv/bin/python`
인지 확인합니다. 패키지가 없다는 오류가 발생해도 곧바로 모델 실패로
기록하지 말고, 먼저 잘못된 가상환경이 선택되지 않았는지 확인합니다.

### Step 0-2. 단독 API 호출 확인

전체 에이전트를 실행하기 전에 모델 연결 자체를 확인합니다.

```bash
timeout 120s ./.venv/bin/python test_upstage.py
```

Solar Open 2의 첫 응답은 네트워크와 생성량에 따라 30초를 넘을 수 있습니다.
짧은 timeout만으로 API 실패를 판정하지 말고, 최초 검증에는 최소 120초를
허용합니다. 전체 에이전트 실행은 도구 호출과 코드 실행 시간을 고려해 이보다
더 긴 제한을 사용합니다. timeout이 발생하면 즉시 역할 실패로 확정하지 않고
`model_api` 또는 네트워크 후보로 기록한 뒤, 합리적인 backoff를 적용한 재시도
결과와 실제 경과 시간을 함께 남깁니다. 응답 지연과 재시도 횟수 자체는 운영
지표로 보존합니다.

다음 항목을 기록합니다.

- 실제 사용 모델명: `solar-open2`
- API 호출 성공 여부와 오류 코드
- 첫 응답까지의 시간
- tool calling 및 structured output 지원 여부
- rate limit 또는 인증 오류

이 단계가 실패하면 에이전트 평가를 시작하지 않습니다. 연결 실패를
Navigator나 Coder의 성능 실패로 기록해서는 안 됩니다.

### ✅ 사전 준비 완료 조건

- [ ] `UPSTAGE_API_KEY`가 코드나 로그에 노출되지 않음
- [ ] Solar Open 2 단독 호출 성공
- [ ] LangSmith trace 생성 확인
- [ ] Gemini와 Solar의 프로젝트가 분리됨
- [ ] 실행 모델과 패키지 버전 기록

---

## 🟢 Mission 1 — 역할별 기준선과 프롬프트 튜닝

### 목표

원본 [`Mission.md`](Mission.md)의 학습 흐름을 유지합니다. 먼저 동일한
프롬프트로 Supervisor, Navigator, Coder의 역할별 기준선을 짧게 측정한 뒤,
실패 trace를 분석해 **프롬프트만 수정**하고 같은 조건에서 전후 결과를
비교합니다. 같은 설정을 대량 반복하는 것보다 다음 순서를 우선합니다.

```text
Level 1 기준선 → 역할별 실패 분석 → 프롬프트 튜닝
→ 동일 조건 전후 비교 → Level 2 일반화 확인
```

1단계 기준선은 모델의 우열을 통계적으로 확정하기 위한 본 실험이 아니라,
Solar Open 2가 어느 역할에서 어떤 문제를 보이는지 찾아 2단계 튜닝 대상을
선정하기 위한 탐색 실험입니다.

### Step 1. 기준 시나리오 선택

파일럿에서는 외부 변수와 난이도를 나눌 수 있도록 다음 네 시나리오를
권장합니다.

| 단계 | 시나리오 | 평가하려는 능력 |
|---|---|---|
| Level 1 | `quotes_01_pagination.md` | 정적 페이지, 반복 수집 |
| Level 1 | `quotes_02_tag_filter.md` | 조건 이해, 필터 준수 |
| Level 2 | `ajax_01_playwright_wait.md` | 동적 로딩과 대기 전략 |
| Level 2 | `ajax_02_api_reverse_engineering.md` | API 탐색과 전략 선택 |

`tests/test_config.yaml`에서 실행할 시나리오만 활성화합니다. Level 1에서
평가 경로가 정상 작동하는지 확인한 뒤 Level 2로 확장합니다.

실제 사이트는 실행 중 변경될 수 있습니다. 가능하면 동일 콘텐츠의 고정
HTML/API fixture를 함께 두어 다음 두 결과를 구분합니다.

- **고정 환경 평가:** 모델·프롬프트·도구 사용 능력
- **라이브 환경 평가:** 사이트 변화와 네트워크에 대한 적응력

### Step 2. 1단계 — 역할별 기준선 10회

Level 1 시나리오 2개에서 아래 5조건을 각각 한 번 실행합니다.

| 조건 | Supervisor | Navigator | Coder | 평가 목적 |
|---|---|---|---|---|
| `GGG` | Gemini | Gemini | Gemini | 기준선 |
| `SSS` | Solar | Solar | Solar | Solar 전체 팀 |
| `SGG` | Solar | Gemini | Gemini | Solar의 위임·조정 능력 |
| `GSG` | Gemini | Solar | Gemini | Solar의 탐색·Blueprint 능력 |
| `GGS` | Gemini | Gemini | Solar | Solar의 코드 생성·실행·복구 능력 |

총 실행 수는 다음과 같습니다.

```text
Level 1 시나리오 2개 × 모델 조건 5개 × 1회 = 10회
```

다섯 조건을 한 시나리오에서 모두 실행한 묶음을 하나의 **비교 세트**라고
부릅니다. 실행 횟수를 집계할 때는 조건 하나를 개별 실행 1회로 셉니다.

모델 설정은 전역 환경 변수 하나로 모든 역할을 바꾸기보다 역할별 명시적
인자로 전달합니다. 각 trace에는 최소한 다음 metadata를 포함합니다.

```text
scenario_id
condition         # GGG, SSS, SGG, GSG, GGS
run_id
model_supervisor
model_navigator
model_coder
site_mode         # fixture 또는 live
```

#### 1단계 실행 완료 기록 — 2026-07-28

두 Level 1 시나리오에서 계획한 10회를 완료했습니다. 상세 run ID, 시간,
모델, 토큰, 오류와 artifact는
[`logs/mission-1.md`](logs/mission-1.md)에 보존합니다.

| 조건 | 정상 종료 | Partial | 평균 시간 | 1단계 관찰 |
|---|---:|---:|---:|---|
| `GGG` | 1 | 1 | 89.218초 | pagination 결과 생성 후 recursion limit 25 |
| `SSS` | 1 | 1 | 228.553초 | tag filter 결과 생성 후 recursion limit 60, 가장 느림 |
| `SGG` | 2 | 0 | 86.360초 | 두 시나리오 모두 정상 종료 |
| `GSG` | 2 | 0 | 85.262초 | 두 시나리오 모두 정상 종료, 가장 빠른 평균 |
| `GGS` | 2 | 0 | 104.398초 | 두 시나리오 모두 정상 종료 |

전체 집계는 `success 8`, `partial 2`, `failed 0`입니다. 두 partial 실행도
요구한 결과 파일과 레코드는 생성했으나 Supervisor workflow가 반복을
끝내지 못해 `GraphRecursionError`로 종료했습니다. 각 조건을 한 번씩만
실행했으므로 이 표를 성공률이나 모델 우열의 통계적 결론으로 해석하지
않습니다.

### Step 3. 2단계 준비 — 실패 분석과 대표 조건 3개 선정

원본 `Mission.md`의 프롬프트 튜닝 목표에 따라 1단계 trace에서 다음을
분석합니다.

- Supervisor가 결과 파일 생성 뒤에도 작업을 반복한 이유
- Navigator의 Blueprint가 Coder 입력에 정확히 전달됐는지
- Coder가 결과 검증 후 완료 신호를 명확히 반환했는지
- 코드 오류와 사이트·API 환경 오류를 구분했는지
- 프롬프트의 어떤 문장이 잘못된 반복, 조기 완료 또는 불필요한 호출을
  유발했는지

모든 5조건을 다시 실행하지 않고 정보량이 큰 3조건을 선택합니다. Round 1은
실패 진단을 위해 다음 조건을 사용했습니다.

| 조건 | 선택 이유 | 주로 관찰할 역할 |
|---|---|---|
| `SSS` | 가장 느리고 recursion partial 발생 | Solar 전체 팀과 종료 조정 |
| `GGS` | Solar Coder를 격리하면서 정상 종료 | 코드 생성·검증·완료 신호 |
| `GSG` | 가장 빠른 정상 종료 조건 | Navigator 안정 기준선 |

Round 1에서도 `SSS`가 올바른 13건을 만들고 recursion partial이 반복되어,
종료 실패는 두 번 관찰됐습니다. 진단 목적을 달성했으므로 Round 2부터는
성능 중심 혼합 구성인 `GGG`, `GGS`, `GSG`로 바꿉니다. `GGG`는 튜닝된
Gemini 기준선, `GGS`와 `GSG`는 각각 Solar Coder와 Navigator의 역할 격리
성능을 보여줍니다. 조건 변경 시점 이후에는 SSS의 회차 간 직접 비교를
종료하며, 변경 이유와 비교 한계를 상세 로그에 남깁니다.

### Step 4. 2단계 — 3회차 프롬프트 개선 실험

2단계는 총 3회차로 진행합니다. Round 1은 `SSS`, `GGS`, `GSG`, Round
2부터는 `GGG`, `GGS`, `GSG`를 같은 Level 1 진단 시나리오에 한 번씩
실행하므로 기본 유효 실행 수는 9회입니다.

```text
대표 조건 3개 × 개선 회차 3회 = 9개 개별 실행
```

시나리오는 1단계에서 실패가 재현됐고 세 조건을 직접 비교할 수 있는 하나를
선정해 3회차 동안 고정합니다. runner, 도구, 모델, temperature, timeout도
고정합니다. 회차 사이에는 `app/prompts/`의 시스템 프롬프트만 수정합니다.

각 회차는 다음 순서를 반드시 지킵니다.

```text
현재 회차의 대표 3조건 실행
→ 결과·trace·결정론 지표 분석
→ 역할별 프롬프트 변경안 제안
→ 근거와 예상 부작용 기록
→ 다음 prompt version 적용
```

| 단계 | 입력 프롬프트 | 실행 후 해야 할 일 |
|---|---|---|
| 2단계 사전 분석 | 기준선 `v0` | 10회 결과로 `v1` 변경안 제안·적용 |
| 1회차 | `v1` | 결과 분석 후 `v2` 변경안 제안·적용 |
| 2회차 | `v2` | `v1` 대비 분석 후 `v3` 변경안 제안·적용 |
| 3회차 | `v3` | 누적 분석 후 최종 후보 `v4` 변경안 제안·적용 |

3회차마다 결과를 보지 않고 미리 정한 문구를 기계적으로 추가하지 않습니다.
각 변경안은 실제 실패, 불필요한 호출, 지연 또는 정확성 변화와 연결돼야
합니다. 개선된 지침도 다른 역할이나 조건의 성능을 악화시키면 되돌리거나
더 좁게 수정합니다.

| 파일 | 튜닝 목표 예시 |
|---|---|
| `app/prompts/supervisor.py` | 결과 검증 후 명시적으로 종료하고 동일 작업 재위임 금지 |
| `app/prompts/navigator.py` | URL/API 패턴 우선 확인, Blueprint 완료 기준 명시 |
| `app/prompts/coder.py` | 결과 파일 검증, 코드 오류와 외부 환경 오류 구분, 완료 신호 명시 |

한 번에 여러 지침을 무분별하게 바꾸지 않습니다. 각 변경에는 다음을
기록합니다.

```text
prompt_version
변경 파일과 문장
관찰된 실패 근거
기대 효과
예상 부작용
적용 조건
```

각 회차 분석과 제안은
[`logs/mission-1.md`](logs/mission-1.md)에 아래 항목으로 기록합니다.

```text
round_id
prompt_version_before / prompt_version_after
3조건의 결과·시간·토큰·호출·오류
직전 회차 및 v0 기준선과의 차이
변경 제안과 trace 근거
채택·보류·되돌림 결정
다음 회차에서 확인할 가설
```

### Step 5. 최종 프롬프트와 Level 2 도전

3회차까지의 비교 항목은 결과 정확성, 정상 종료, recursion 발생 여부,
시간, 호출 수, 토큰과 재시도입니다. 최종 후보 `v4`에는 3회차 분석에 따른
변경을 반영합니다.

`v4`를 동결한 뒤 Level 2 대표 시나리오 1개에 도전합니다. 이 실행은
3회차 뒤 제안한 최종 변경을 검증하고, Level 1 개선이 동적 환경에도
일반화되는지 확인하는 단계입니다. Level 2 결과를 보고 다시 같은
시나리오에 맞춘 프롬프트를 반복 수정하지 않습니다.

#### 선택적 Sequential 진단

Supervisor의 영향을 제거해야 원인을 구분할 수 있을 때만 다음 경로를
사용합니다.

```bash
./.venv/bin/python -m tests.run_sequential_scenarios
```

Navigator의 최종 Blueprint가 실제 Coder 입력에 전달되고, 두 에이전트가
같은 scenario ID와 run ID를 공유하며, 실패 상태가 역할별로 분리될 때만
`Navigator → Coder` 파이프라인 결과로 인정합니다.

### Step 6. 실행 결과 보존

각 실행은 고유한 경로에 저장해야 하며 이전 결과를 덮어쓰지 않습니다.

```text
artifacts/results/
└── <scenario_id>/
    └── <condition>/
        └── <run_id>/
            ├── result.json
            ├── execution.log
            ├── evaluation.json
            └── metadata.json
```

`run_id`는 최소한 실행 시각과 반복 번호를 포함합니다.

### Step 7. 결정론적 결과 채점

현재 JSON Schema 검사는 출력 형식을 확인하지만 값의 정확성을 보장하지
않습니다. 각 시나리오에 작은 gold dataset 또는 검증 규칙을 준비합니다.

#### 필수 지표

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

권장 종합 가중치는 다음과 같습니다.

| 평가 영역 | 비중 |
|---|---:|
| 내용 정확성·완전성 | 40% |
| 작업 완료 | 20% |
| 형식 정확성 | 20% |
| 전략 효율 | 10% |
| 비용·지연·재시도 | 10% |

내용 정확성, 작업 완료와 형식 정확성은 코드로 판정합니다. LLM Judge는
전략 해석과 개선 피드백에만 사용하며 단독 합격 기준으로 삼지 않습니다.

### Step 8. 에이전트 운영 지표

LangSmith trace와 실행 metadata에서 다음을 수집합니다.

- 전체 완료 시간
- 첫 모델 응답 및 첫 tool call까지의 시간
- 입력·출력 토큰
- 추정 API 비용
- 모델 호출과 tool call 횟수
- Supervisor와 하위 에이전트 사이의 왕복 횟수
- 코드 실행과 수정 횟수
- 재시도 횟수
- 사람이 개입한 횟수
- rate limit 및 API 오류

성공했더라도 기준선보다 호출·비용·시간이 현저하게 큰 경우 운영상 차이를
별도로 해석합니다.

### Step 9. 실패 유형 분류

모든 실패는 다음 중 하나 이상의 유형으로 기록합니다.

| 실패 유형 | 예시 |
|---|---|
| `instruction` | 목표, 필터 또는 저장 경로 오해 |
| `orchestration` | Supervisor가 역할을 잘못 위임하거나 완료를 조기 선언 |
| `navigation` | 잘못된 URL·selector·렌더링 전략 |
| `structured_output` | Blueprint 또는 JSON 형식 생성 실패 |
| `coding` | 문법, import, 런타임 오류 |
| `recovery` | 오류 원인을 찾지 못하거나 같은 실패 반복 |
| `persistence` | 결과 파일 누락 또는 잘못된 경로 저장 |
| `content` | 스키마는 맞지만 값이 틀리거나 누락됨 |
| `site_environment` | 사이트 변경, 차단, 네트워크 장애 |
| `model_api` | 인증, timeout, rate limit, 공급자 오류 |
| `evaluator` | Judge 파싱 또는 채점 실패 |

`site_environment`, `model_api`, `evaluator` 오류는 에이전트 능력 실패와
분리해 집계합니다.

### Step 10. 결과 판정

시나리오·조건별로 다음을 계산합니다. 1단계는 조건당 표본이 1개이므로
성공률 대신 관찰 결과로 표현합니다.

- `pass@1`: 첫 실행 성공 여부
- 부분 성공률
- 완료 시간, 토큰과 비용
- 역할별 실패 유형 분포
- 튜닝 전후 정상 종료·정확성·시간·호출 변화

선택적 반복을 수행했을 때만 성공률, 중앙값과 반복 간 편차를 계산합니다.
표본 1회의 값을 일반적인 성공률이나 모델 성능으로 표현하지 않습니다.

최종 결론은 하나의 종합 점수보다 역할별로 작성합니다.

```text
Supervisor: 위임, 진행 판단, 재시도 조정
Navigator: 탐색 전략, selector/API 발견, Blueprint 정확성
Coder: 코드 생성, 실행, 디버깅, 결과 저장
```

### ✅ Mission 1 산출물

- [x] Solar Open 2 API 연결 검증 기록
- [x] Level 1 두 시나리오의 5조건 기준선 10회
- [x] 10회 trace 기반 역할별 실패 분석
- [x] 대표 조건 3개 선정과 근거
- [x] 1회차 실행 분석과 `v2` 프롬프트 변경 제안
- [x] 2회차 실행 분석과 `v3` 프롬프트 변경 제안
- [x] 3회차 실행 분석과 최종 `v4` 프롬프트 변경 제안
- [x] 회차별 프롬프트 변경·채택·되돌림 이력
- [x] 최종 프롬프트를 동결한 Level 2 도전 — v4로 GGG/GGS/GSG 실행
- [x] 고유 run ID가 있는 원본 로그와 결과
- [x] 결정론적 정확도 지표
- [x] LangSmith 운영 지표
- [x] 역할별 실패 분석과 중간 결론

---

## 🟡 Mission 2 — Analyst 에이전트 구축

### 목표

원본 [`Mission.md`](Mission.md)의 점진적 빌드업을 따릅니다. Mission 1에서
수집한 JSON을 분석하고 차트, Markdown 보고서와 Gemini 인포그래픽을 만드는
Analyst를 직접 설계·구현한 뒤 기존 파이프라인에 연결합니다. 기본 Analyst와
전체 파이프라인은 Gemini로 완성합니다. 이후 분석 코드 계획이나 근거 기반
보고서 작성처럼 중요한 텍스트 노드만 Solar Open 2로 교체해 A/B 비교합니다.
반복 모델 평가보다 **원본 미션의 새 역할과 도구를 완성하고 실제 수집
결과를 끝까지 처리하는 것**을 우선합니다.

```text
Supervisor → Navigator & Coder → JSON
                                  ↓
                              Analyst
                                  ↓
                         통계 + 차트 + 보고서
```

### Step 1. Analyst 역할과 도구 설계

먼저 Analyst가 맡을 책임과 도구의 입력·출력·실패 형태를 설계합니다.

| 도구 | 역할 | 입력 | 출력 | 결정론적 확인 |
|---|---|---|---|---|
| `load_json_data` | JSON/CSV 로드와 프로파일링 | 안전한 상대 경로 | 레코드·필드·누락 요약 | 원본과 개수 비교 |
| `run_analysis_code` | pandas 기반 계산 | 제한된 분석 코드 | 계산 결과 텍스트/JSON | gold 값과 비교 |
| `create_chart` | 결정론적 차트 코드 실행 | 데이터·차트 명세·파일명 | 저장 경로 | 파일·축·레이블 |
| `generate_infographic` | Gemini/Nano Banana 이미지 생성 | 근거 데이터·프롬프트·파일명 | 이미지 경로 | 파일 존재·입력 근거 |
| `write_report` | 근거 기반 Markdown 보고서 | 계산 결과와 인사이트 | 저장 경로 | 필수 섹션·수치 근거 |

`create_chart`는 matplotlib 등 결정론적 Python 라이브러리가 구조화
데이터로 파일을 렌더링합니다. `generate_infographic`와 이미지
해석·Vision/OCR 도구는 Gemini가 담당합니다. B 조건에서도 이 단계는
Gemini로 고정하고, Solar는 선택한 텍스트 노드의 입력과 출력만 처리합니다.

### Step 2. Analyst 도구 구현

`app/tools/analyst.py`에 도구를 구현합니다. 입력 파일과 출력 파일은 허용된
artifact 디렉터리 안으로 제한하고, 임의의 시스템 명령이나 네트워크 호출을
허용하지 않습니다. 계산 결과는 가능한 한 JSON처럼 다시 검증할 수 있는
형태로 반환합니다.

### Step 3. Gemini 기본 Analyst 생성

먼저 원본 `Mission.md`대로 Gemini가 분석, 도구 조정, 차트와 보고서까지
완주하는 Analyst를 만듭니다. 선택 과제를 수행할 때는 Gemini
인포그래픽까지 연결합니다. 이후 특정 텍스트 노드에만 대체 모델을 주입할
수 있도록 factory를 설계합니다.

```python
def create_analyst_agent(
    model_name: str = "google_genai:gemini-flash-latest",
    model_provider: str | None = None,
    text_experiment_model: str | None = None,
    text_experiment_provider: str | None = None,
    temperature: float = 0.1,
):
    ...
```

`model_name`은 기본 Gemini orchestration을 담당합니다. B 조건에서만
`text_experiment_model="solar-open2"`,
`text_experiment_provider="upstage"`를 지정합니다. Solar를 Analyst 전체
모델로 바꾸지 않고 사전에 선택한 텍스트 노드만 대체합니다.

`app/prompts/analyst.py`에는 다음 지침을 포함합니다.

- 입력이나 계산 결과에 없는 수치를 만들지 않기
- 계산은 추측하지 말고 도구로 실행하기
- 모든 보고서 수치를 계산 결과와 연결하기
- 차트 파일 생성 뒤 경로와 사용한 x/y 필드를 명시하기
- A/B 텍스트 노드의 출력 schema와 입력 근거를 동일하게 유지하기
- 인포그래픽과 Vision 단계는 두 조건 모두 Gemini로 실행하기
- 인포그래픽의 수치도 계산 결과에 근거하기

### Step 4. 파이프라인 연동

먼저 원본 미션의 간단한 방법으로 Analyst를 독립 호출해 도구와 산출물을
검증합니다.

```text
기존 수집 JSON → Analyst → 통계 + 차트 파일 + Markdown 보고서
```

독립 호출이 안정적으로 성공한 뒤에만 Supervisor에 `chat_to_analyst`
도구를 추가해 전체 파이프라인으로 확장할 수 있습니다.

```text
Supervisor → Navigator & Coder → JSON → Analyst → 보고서
```

Supervisor 연동을 선택하면 Mission 1의 동작이 바뀌지 않도록 Analyst 없는
기존 경로를 유지하고, 설정으로 Analyst 사용 여부를 선택할 수 있게 합니다.
기본과 A/B 조건 모두 Gemini가 전체 파이프라인과 인포그래픽 생성을
담당합니다. B 조건은 지정한 텍스트 노드의 호출만 Solar로 라우팅합니다.

### Step 5. 고정 데이터와 실제 수집 데이터 확인

먼저 정답을 계산할 수 있는 작은 고정 JSON으로 도구와 Analyst의 정확성을
확인하고, 그다음 Mission 1의 실제 수집 JSON을 분석합니다.

- 레코드 수와 누락값
- 그룹별 개수·평균·최댓값·최솟값
- 상위 N개 항목
- 중복 레코드
- 날짜 또는 가격 정렬
- 차트에 사용될 x/y 값

고정 데이터는 구현 오류와 모델 오류를 구분하기 위한 fixture이며, 동일
입력을 무조건 여러 번 반복하는 것이 기본 목표는 아닙니다. Gemini 기본
파이프라인을 먼저 1회 확인한 뒤, 아래 텍스트 노드 중 중요도가 높은 하나
또는 둘을 선정해 A/B 각 1회 실행합니다.

| A/B 후보 텍스트 노드 | A 조건 | B 조건 | 비교 지표 |
|---|---|---|---|
| 분석 계획·pandas 코드 작성 | Gemini | Solar Open 2 | 계산 정확성·코드 성공·호출량 |
| 근거 기반 Markdown 보고서 | Gemini | Solar Open 2 | 수치 grounding·필수 섹션·지연 |

두 조건의 입력 데이터, prompt, schema, 도구, temperature와 후속 Gemini
멀티모달 단계를 동일하게 유지합니다. 차이가 불명확하거나 실패 원인을
확인해야 할 때만 선택적으로 반복합니다.

### Step 6. 결과 확인과 평가

| 평가 영역 | 판정 방법 |
|---|---|
| 계산 정확성 | gold 통계와 exact 또는 허용 오차 비교 |
| 근거 충실도 | 보고서 수치가 입력·계산 결과에 존재하는지 확인 |
| 코드 실행 | 생성 분석 코드의 종료 상태 |
| 차트 코드 실행 | 파일과 필수 레이블을 코드로 확인 |
| 선택적 Gemini 인포그래픽 | 실행 시 A/B 모두 동일한 Gemini 단계; 텍스트 노드 비교 점수에서 제외 |
| 해석 품질 | 독립 Judge와 사람 표본 검토 |
| 운영 효율 | 호출, 토큰, 비용, 지연 |

환각된 수치가 하나라도 있으면 별도 `grounding` 오류로 기록합니다.

### ✅ Mission 2 산출물

#### 필수

- [ ] Analyst 도구 설계와 안전한 파일 입출력
- [ ] `app/tools/analyst.py`
- [ ] `app/prompts/analyst.py`
- [ ] `app/agents/analyst.py`
- [ ] Gemini 기본 Analyst 전체 파이프라인
- [ ] 중요 텍스트 노드의 Gemini/Solar A/B 주입 지점
- [ ] 독립 Analyst 실행 경로
- [ ] 고정 데이터와 Mission 1 수집 데이터 실행 결과
- [ ] 결정론적 계산 정확도
- [ ] 코드로 생성한 차트와 텍스트 분석 보고서
- [ ] 근거 없는 수치 및 실패 유형 기록

#### 권장·선택

- [ ] Supervisor의 선택 가능한 Analyst 연동 경로
- [ ] Gemini/Nano Banana 기반 인포그래픽
- [ ] 멀티모달을 실행한 경우 고정된 Gemini 결과와 텍스트 노드 A/B 결과 분리

---

## 🔴 Mission 3 — 에이전트 고도화 (선택 미션)

원본 [`Mission.md`](Mission.md)의 네 트랙 중 하나 이상을 선택해 실제
기능을 구현합니다. 모든 트랙을 대규모 비교 실험으로 수행하는 것이 필수는
아닙니다. 선택한 기능이 기존 기준선에 섞이지 않도록 Mission 1·2 결과와
프롬프트 version을 먼저 동결하고, 적용 전후를 작은 검증 시나리오로
확인합니다.

Mission 3도 먼저 Gemini로 선택 트랙 전체를 완성합니다. 그다음 해당
기능에서 중요한 텍스트 판단 노드 하나를 골라 Gemini(A)와 Solar Open
2(B)를 교체 비교합니다. 나머지 orchestration, 도구와 멀티모달 단계는 두
조건 모두 Gemini로 고정합니다.

### Track A. 학습하는 에이전트 — Pattern Memory

실행 경험의 성공·실패 패턴을 `pattern_memory.json`에 자동 기록하고,
미들웨어가 다음 실행의 시스템 프롬프트에 관련 패턴만 주입하는 지속적 학습
경로를 구현합니다.

- 저장 항목: domain, strategy, selector/API pattern, 실패 원인, 복구 결과
- 비밀값과 전체 모델 reasoning은 저장하지 않음
- 다음 시나리오와 관련 있는 패턴만 선택
- 중복·오래된·실패한 패턴의 갱신 규칙 정의

검증 시 Memory 없음과 동일 snapshot 제공 조건을 비교합니다. 누적 Memory는
실행마다 상태가 달라지므로 별도 학습 데모로 기록하며 고정 조건 평가와
섞지 않습니다.

### Track B. Model Fallback 미들웨어

timeout, rate limit, 공급자 오류 또는 명시한 품질 실패가 발생했을 때 대체
모델로 전환하는 미들웨어를 구현합니다.

- Solar 단독 평가에서는 fallback을 비활성화합니다.
- fallback 발생 여부와 전환 사유를 기록합니다.
- fallback 뒤 성공한 실행은 `recovered_by_fallback`으로 표시합니다.
- 해당 성공을 Solar 단독 성공률에 포함하지 않습니다.
- 기본 운영 경로는 Gemini → Solar로 구현합니다.
- Solar → Gemini 역방향은 필요할 때만 별도 복구 진단으로 실행합니다.

정상적인 느린 Solar 응답을 실패로 오판하지 않도록 Solar timeout은 Mission
1의 여유 있는 정책을 사용합니다.

### Track C. Skill System 적용

`app/skills/`에 도메인별 지침을 두고 현재 시나리오에 필요한 Skill만
동적으로 로드해 시스템 프롬프트에 제공합니다.

- Skill 이름, 적용 도메인, 입력 조건과 기대 전략을 명시
- 적용한 Skill ID/version을 metadata에 기록
- 관련 없는 Skill을 기본으로 모두 주입하지 않음
- Skill 없음과 필요한 Skill 제공 조건을 비교

선택적으로 관련 없는 Skill이 많은 조건도 실행해 긴 컨텍스트에서 올바른
지침을 선택하는지 확인할 수 있습니다.

### Track D. 사용자 정의 시나리오 작성과 도전

실무에서 수집하고 싶은 공개 데이터 소스를 정하고
`artifacts/scenarios/`에 검증 가능한 시나리오를 작성해 도전합니다.

- 로그인 없이 접근 가능
- 서비스 약관과 robots 정책을 준수
- 결과 정답 또는 검증 규칙을 만들 수 있음
- 너무 자주 변경되지 않는 공개 데이터
- 정적·동적·다단계 난이도를 명확히 구분 가능

시나리오에는 목표, 예상 Schema 외에 gold 값, 필수 레코드, 허용 오류와
환경 실패 판정 기준을 포함합니다.

### 진행 방식

1. 네 트랙 중 하나 이상을 선택하고 선택 이유를 기록합니다.
2. Gemini 기본 조건에서 기능을 구현하고 작은 단위 테스트로 검증합니다.
3. Gemini 전체 파이프라인으로 대표 시나리오를 완주합니다.
4. 중요한 텍스트 노드 하나와 동일 입출력 schema를 A/B 경계로 선정합니다.
5. A는 Gemini, B는 Solar Open 2를 사용하고 그 밖의 모든 단계를 고정합니다.
6. 해당 노드의 정확성, 지연, 비용과 downstream 영향을 Wiki에 기록합니다.
7. 차이가 불명확할 때만 선택적으로 반복합니다.

트랙별 A/B 후보는 다음과 같습니다.

| 트랙 | Gemini로 완성할 기본 기능 | Solar로 교체할 수 있는 텍스트 노드 예시 |
|---|---|---|
| Pattern Memory | 기록·검색·프롬프트 주입 전체 | 현재 시나리오에 맞는 Memory 선택·요약 |
| Model Fallback | 오류 감지·전환·복구 전체 | 복구 전략 또는 오류 원인 분류 |
| Skill System | Skill 저장·검색·주입 전체 | 필요한 Skill 선택 또는 적용 계획 |
| 사용자 시나리오 | 탐색·수집·분석 전체 | 수집 전략 계획 또는 결과 요약 |

Fallback 트랙에서 실제 대체 모델로 Solar를 사용하는 운영 복구와, 위 표의
텍스트 노드 A/B는 구분합니다. fallback으로 전환된 실행은 모델 품질 A/B
표본이 아니라 `recovered_by_fallback`으로 기록합니다.

### ✅ Mission 3 산출물

- [ ] 고도화 전 baseline 동결
- [ ] 선택한 트랙과 선택 이유
- [ ] Gemini 기본 조건의 구현 코드와 단위 검증
- [ ] Gemini 전체 파이프라인 완주 결과
- [ ] 중요한 텍스트 노드의 Gemini/Solar A/B 경계와 선정 근거
- [ ] A/B 실행 기록
- [ ] 효과·부작용·운영 지표 분석
- [ ] Fallback 선택 시 Solar 단독 성공과 복구 성공 분리
- [ ] 사용자 시나리오 선택 시 gold/검증 규칙 포함

---

## 📊 최종 결과 보고서 템플릿

```markdown
# AAWS 기본 미션과 Solar Open 2 A/B 실험

## 실행 환경
- 모델 및 provider:
- LangChain/LangGraph/langchain-upstage 버전:
- 시나리오:
- prompt version과 실행 수:
- fixture/live 구분:

## Mission 1 — 기준선과 프롬프트 튜닝
| 조건 | 상태 | 내용 정확도 | 시간 | 토큰 | 실패 유형 |
|---|---|---:|---:|---:|---|
| GGG | | | | | |
| SSS | | | | | |
| SGG | | | | | |
| GSG | | | | | |
| GGS | | | | | |

### 회차별 프롬프트 변경
| 회차 | before → after | 변경 근거 | 결과 변화 | 채택/되돌림 |
|---|---|---|---|---|
| | | | | |

## Mission 2 — Gemini 기본 구현
- Analyst 도구와 파이프라인:
- 차트와 보고서:
- 선택적 Supervisor 연동:
- 선택적 Gemini 멀티모달 산출물:

### 핵심 텍스트 노드 A/B
| 노드 | A: Gemini | B: Solar | 정확성/grounding | 시간·비용 | 결론 |
|---|---|---|---:|---:|---|
| | | | | | |

## Mission 3 — 선택 트랙
- 선택 트랙과 이유:
- Gemini 기본 구현 결과:
- 선택한 텍스트 A/B 노드:

| 조건 | 모델 | 결과 | 시간·비용 | downstream 영향 |
|---|---|---|---:|---|
| A | Gemini | | | |
| B | Solar Open 2 | | | |

## 실패 유형
| 조건 | 주요 실패 | 횟수 | 모델/환경 구분 |
|---|---|---:|---|
| | | | |

## 결론
- Supervisor:
- Navigator:
- Coder:
- Analyst:
- Mission 3 선택 기능:

## 운영 판단
- 적합한 역할:
- 주의가 필요한 역할:
- 필요한 guardrail:
- 비용·지연 trade-off:

## 한계
- 외부 사이트 변동:
- 반복 수:
- Judge 편향:
- 미측정 항목:
```

실행하지 않은 조건은 임의의 수치를 채우지 않고 `N/A`로 기록합니다.

---

## 📎 빠른 참조

### 현재 바로 실행 가능한 명령

```bash
# Solar API 단독 연결
timeout 120s ./.venv/bin/python test_upstage.py

# Gemini 전체 팀
./.venv/bin/python -m tests.run_supervisor_scenarios --model-mode gemini

# Solar 전체 팀
./.venv/bin/python -m tests.run_supervisor_scenarios --model-mode upstage

# Gemini와 Solar 전체 팀 순차 실행
./.venv/bin/python -m tests.run_supervisor_scenarios --model-mode both

# Mission 1 역할별 runner
./run_local_python.sh -m tests.run_mission1 --help
```

### Mission 1 runner에서 구현된 기능

- 역할별 모델 조합: `GGG`, `SSS`, `SGG`, `GSG`, `GGS`
- 반복 수와 run ID 지정
- fixture/live 모드
- 결과 덮어쓰기 방지
- gold data 기반 결정론적 채점
- 모델·역할별 LangSmith metadata

Mission 2·3 runner와 텍스트 노드 A/B 주입 기능은 해당 Mission에서
구현합니다. 아직 구현하지 않은 명령을 빠른 참조에 임의로 적지 않습니다.
