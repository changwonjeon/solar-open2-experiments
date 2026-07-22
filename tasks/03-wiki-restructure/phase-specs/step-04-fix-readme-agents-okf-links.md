```
확정된 현재 filesystem을 기준으로 README, AGENTS, OKF index/log와 내부 링크를 정합화해줘.

중요: filesystem을 문서에 맞추지 말고, 승인된 실제 filesystem을 기준으로 문서를 고쳐라.

## 수정 대상

- `README.md`
- `AGENTS.md`
- `docs/AGENTS.md`
- `docs/index.md`
- `docs/log.md`
- `docs/experiment-log.md`
- 각 task의 README/index/AGENTS/CLAUDE
- 각 Wiki 하위 `index.md`
- 실제 구조 변경으로 깨진 Markdown 상대 링크
- 회의록 문서의 `input_sources`

## 반드시 수정할 항목

### README

현재 `tasks/` 구조를 정확히 표시하라.

다음 옛 경로를 제거하거나 역사 설명으로만 남겨라.

- `projects/ralph-loop/`
- `docs/experiments/ralphthon/`
- `docs/experiments/meeting-minutes/`
- 존재하지 않는 전역 `tests/`, `data/fixtures/`

회의록 input/output 링크는 실제 `tasks/02-meeting-minutes/` 경로를 사용하라.

### 루트 AGENTS

Source / Wiki / Schema를 현재 구조에 맞게 다시 정의하라.

- 각 task의 `source/`: Source 계층
- 각 task의 `docs/`: task-local Wiki 계층
- 각 task의 `output/`: 생성 산출물
- 루트 `docs/`: 프로젝트 공통 Wiki
- 루트와 task의 AGENTS/CLAUDE: Schema

migration 중에만 허용되는 이동과 평상시 Source 불변성을 구분하라.

### docs/index.md

현재 파일은 과거 experiments index 내용으로 잘못 덮여 있다.
루트 Docs bundle index로 다시 작성하라.

반드시 포함할 것:

- `guide/`
- `reference/`
- `notes/`
- `templates/`
- `experiment-log.md`
- `log.md`
- `../tasks/01-ralpthon/`
- `../tasks/02-meeting-minutes/`

`docs/index.md`에서 task 링크는 반드시 `../tasks/...` 형식이어야 한다.

존재하지 않는 다음 링크는 제거하거나 "planned, non-link"로 표시하라.

- model-tests
- benchmarks
- usage-studies
- integration-tests
- people/researchers
- people/engineers
- people/professors
- people/startup-founders
- people/vcs

회의록 실험을 "시작 전"이라고 표시하지 마라.

### docs/log.md

다음을 기록하라.

- `7024b1b` 구조 개편
- 발견된 Source 누락
- `tasks/` 재편
- 복구한 고유 blob 수
- canonical 경로
- 제거한 중복
- 현재 task 구조
- 검증 결과

기존 역사 기록의 경로를 무조건 현재 경로로 바꾸지 마라.
과거 당시 경로라면 원래 경로를 유지하고, 현재 위치를 별도로 표시하라.

중복된 7월 19일 항목은 내용 손실 없이 하나로 통합하라.

### OKF

Wiki 콘텐츠의 모든 Markdown에 parse 가능한 YAML frontmatter와 비어 있지 않은 `type`을 적용하라.

최소 대상:

- `docs/index.md`
- `docs/log.md`
- `docs/experiment-log.md`
- guide/reference/notes의 실제 index
- task별 Wiki index
- task별 Wiki 문서

`AGENTS.md`와 `CLAUDE.md`는 Schema 파일이므로 OKF 콘텐츠 검사에서 제외한다고 규칙에 명시하라. `CLAUDE.md`에는 frontmatter를 추가하지 마라.

### 회의록 provenance

회의록의 `input_sources`를 실제 경로에 맞춰라.

현재 문서 위치가
`tasks/02-meeting-minutes/docs/meeting-minutes/`이므로,
가능하면 문서 기준 상대 경로를 사용하라.

예:

`../../source/original/<파일명>`

존재하지 않는 `projects/meeting-minutes/...` 경로는 제거하라.

### 링크 lint

Markdown code fence 안의 예제와 다음 placeholder는 실제 broken link로 계산하지 마라.

- `url`
- `.*`
- `*.md`
- 작성 예시용 `<...>`
- 명시적으로 planned라고 표시된 미래 문서

링크를 다음으로 분류하라.

1. 실제 broken link
2. template placeholder
3. planned document
4. archive의 역사적 경로
5. 외부 URL

실제 broken link만 수정하라.
작성되지 않은 문서를 링크 대상으로 만들기 위해 빈 파일을 생성하지 마라.

## 보호 범위

- Source 파일 내용 수정 금지
- 실행 코드 수정 금지
- 회의록 본문과 LinkedIn output 본문 수정 금지
- `_private/`, `_inbox/`, result 파일 수정 금지
- git add, commit, push 금지

## 검증

- 실제 Wiki 콘텐츠 OKF 위반 0
- 실제 broken internal link 0
- README·AGENTS·index에 기재된 경로 존재
- `docs/index.md`가 모든 주요 영역의 진입점을 제공
- 회의록 `input_sources` 대상 존재
- Source blob hash 무변경
- `CLAUDE.md`가 `@AGENTS.md` 한 줄
- `git diff --check` 통과

완료 후 변경 파일, 수정 이유와 lint 결과를 보고하고 멈춰라.
```
