# AAWS + Solar Open 2 실험 기록

이 문서는 2026-07-28에 진행한 Upstage 실험의 현재 상태와 재개 지점을
요약합니다.

- 실험 계획: [`Mission_upstage.md`](Mission_upstage.md)
- Wiki 인덱스: [`log.md`](log.md)
- Mission 1 상세 로그: [`logs/mission-1.md`](logs/mission-1.md)
- 원본 미션: [`Mission.md`](Mission.md)

## 실험 원칙

원본 `Mission.md`의 Gemini 기반 기능과 점진적 학습 흐름을 기본으로
유지합니다. Mission 1에서는 Supervisor, Navigator, Coder 역할별로 Solar
Open 2를 비교했습니다. Mission 2·3에서는 Gemini가 전체 기본 파이프라인을
수행하고, 중요한 텍스트 노드만 Solar Open 2로 교체해 A/B 비교할
계획입니다. 이미지 생성과 Vision 등 멀티모달 단계는 Gemini로 고정합니다.

## 실행 환경

- Workspace: `/home/redux80/_Upstage/tasks/06-practice-aaws/aaws`
- Python: `./.venv/bin/python`
- Solar model/provider: `solar-open2` / Upstage
- `langchain-upstage`: `0.7.7`
- Solar 최초 호출: 성공
- Solar timeout: 단독 검증 120초, 에이전트 run 900초

상위 프로젝트의 `.venv`가 잘못 선택될 수 있으므로 단순 `uv run`보다
저장소의 Python을 직접 사용합니다.

```bash
timeout 120s ./.venv/bin/python test_upstage.py
./run_local_python.sh -m tests.run_mission1 --help
```

API 키, credential과 전체 reasoning content는 로그에 저장하지 않습니다.

## Mission 1 완료 범위

### 1단계 — Level 1 기준선 10회

두 Level 1 시나리오에서 `GGG`, `SSS`, `SGG`, `GSG`, `GGS`를 한 번씩
실행했습니다.

- success: 8
- partial: 2
- failed: 0
- partial 실행도 요구 데이터는 생성했으나 recursion으로 정상 종료하지
  못했습니다.

세 글자는 `Supervisor → Navigator → Coder` 순서이며, `G`는 Gemini,
`S`는 Solar Open 2입니다.

### 2단계 — 프롬프트 튜닝 3회차

고정 시나리오 `quotes_02_tag_filter`에서 회차별 결과를 분석하고 다음
프롬프트를 제안·적용했습니다.

| Version | 변경 | 판단 |
|---|---|---|
| `v1` | Supervisor 명시적 종료, Navigator 도구 예산, Coder 성공 후 종료 | GGS/GSG 시간·호출 개선, SSS recursion 지속 |
| `v2` | Coder 고유 script, create 1회, `create→run→validate`, 최대 6 tool | GGG/GGS/GSG 모두 성공; 최종 기반으로 채택 |
| `v3` | 정적 필터 URL에서 browse 축소 지침 | browse 제거가 재현되지 않고 token 증가 |
| `v4` | Navigator의 v3 문구 rollback | Supervisor v1 + Navigator v2 + Coder v2 구성 |

Round 2부터는 성능 중심 혼합 조건 `GGG/GGS/GSG`를 사용했습니다. SSS는
v0와 v1에서 recursion partial을 두 번 관찰해 진단 비교를 종료했습니다.

### Level 2 — v4 일반화 검증

`ajax_01_playwright_wait`에서 `GGG/GGS/GSG`를 실행했습니다. 실행은 모두
종료됐으며, 원본 평가와 수정된 엄격 평가를 함께 보존했습니다.

| 조건 | 상태 | 시간 | model/tool | tokens | 핵심 관찰 |
|---|---|---:|---:|---:|---|
| `GGG` | partial | 124.438s | 20/16 | 188,944 | 3개 값은 정확하나 `year`를 문자열로 저장해 schema 실패 |
| `GGS` | failed | 180.226s | 27/24 | 35,486 | 불필요한 `playwright install-deps`와 반복 후 결과 미저장 |
| `GSG` | success | 180.471s | 21/18 | 93,434 | strict schema와 gold value 모두 통과 |

GGG의 최초 evaluator는 간이 schema를 엄격히 검사하지 못했고 문자열 year와
정수 gold 비교도 잘못 처리했습니다. 원본 `evaluation.json`은 보존하고,
strict type과 정규화된 gold 비교 결과를 `evaluation_rechecked.json`에
별도로 저장했습니다.

GGS가 실행한 `playwright install-deps chromium`은 OS dependency 설치라
sudo/TTY가 필요합니다. 기존 Playwright 도구가 이미 작동했으므로 설치는
불필요했고, 이 실패는 API나 사이트 문제가 아니라 prompt/tool
orchestration과 persistence 실패로 분류했습니다.

Level 2 artifacts:

- [`GGG run`](artifacts/results/ajax_01_playwright_wait/GGG/20260728T074919.295971Z-r01-8c0a4398/)
- [`GGS run`](artifacts/results/ajax_01_playwright_wait/GGS/20260728T075123.807154Z-r01-e1d3d296/)
- [`GSG run`](artifacts/results/ajax_01_playwright_wait/GSG/20260728T075426.005767Z-r01-326087a6/)

## 현재 중단 상태

- 모든 Mission 1 실행 프로세스 종료
- 현재 prompt: `v4`
- Mission 2: 계획 확정, 미실행
- Mission 3: 계획 확정, 미실행
- Level 2 결과와 실패 artifact 보존 완료

## 재개 시 제안

Level 2 실패를 최초 일반화 결과에서 지우지 않고, 별도 `v5 recovery`
실험으로 구분합니다.

Coder prompt 후보:

1. `sudo`, `apt`, `pip install`, `uv add`, `playwright install`,
   `playwright install-deps` 등 환경 변경 금지
2. dependency 오류가 나면 설치하지 말고 `execution_environment` 오류로 보고
3. 저장 전 schema field type 확인
4. 숫자 문자열을 요구된 integer로 정규화
5. 저장된 JSON을 다시 읽어 타입까지 한 번 검증

`v5`를 실행한다면 GGS만 다시 실행하지 않고 같은
`ajax_01_playwright_wait`에서 `GGG/GGS/GSG` 전체를 새 run ID로 실행해
조건을 맞춥니다. 이 실험은 `v4 Level 2 일반화`가 아니라
`v5 recovery`로 별도 집계해야 합니다.

## Mission 2·3 계획

Mission 2는 Gemini Analyst를 기본으로 완성하고 분석 코드 계획 또는 근거
기반 보고서 같은 중요 텍스트 노드만 Gemini/Solar A/B로 비교합니다.
Supervisor 연동과 Gemini 인포그래픽은 선택 과제입니다.

Mission 3는 Pattern Memory, Model Fallback, Skill System, 사용자 정의
시나리오 중 하나 이상을 Gemini로 먼저 구현합니다. 이후 중요한 텍스트
판단 노드 하나만 Solar로 교체해 A/B 비교합니다. Mission 2·3은 Mission 1
및 선행 Mission의 baseline을 동결한 뒤 순차 실행합니다.
