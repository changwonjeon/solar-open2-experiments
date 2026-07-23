---
type: Execution Specification
title: "Task 05 — Ralphthon 철자 인식 오류 재현 실험"
description: "Solar Open 2와 Claude Code에서 Ralphthon 철자 보존·추론·교정 및 저장소 확산을 재현하기 위한 실행 명세"
tags: [solar-open2, claude-code, ralphthon, spelling, evaluation]
timestamp: 2026-07-24T00:00:00+09:00
status: planned
model: solar-open2
harness: claude-upstage
---

# Task 05 — Ralphthon 철자 인식 오류 재현 실험

## 실행 주체와 기준

이 문서는 `_Upstage` 루트에서 `claude-upstage --model solar-open2`로 시작한 Solar Open 2 + Claude Code 세션이 실행한다.

- 정확한 표기: **Ralphthon**
- canonical slug: `ralphthon`
- 관찰된 잘못된 표기: `Ralpthon`, `ralpthon`
- 조건별 반복 횟수: 10회
- 모델 대조군: 없음. Solar Open 2 내부 조건만 비교한다.
- Git commit과 push: 사용자 별도 승인 전까지 금지한다.

Codex는 이 실행 명세만 작성했다. fixture, 실행기, raw 결과, 채점 결과와 최종 보고서는 이 명세를 실행하는 Solar Open 2 세션의 산출물로 구분한다.

## 해석 원칙

“랄프톤”이라는 한글 음차만 보고 창안자가 선택한 `Ralphthon`을 맞히는 문제에는 언어적으로 유일한 정답이 없다. 따라서 음차-only 조건은 오류율이 아니라 생성 철자 분포로 기록한다.

오류로 판정할 수 있는 대상은 다음과 같다.

1. canonical 철자를 명시했는데 정확히 복사하거나 유지하지 못한 경우
2. authoritative glossary보다 잘못된 다수 표기를 따른 경우
3. 명시적 교정 뒤에도 현재 파일명·경로·본문에 오타가 남거나 재발한 경우

이 실험만으로 `Ralphthon`이 모델의 학습 데이터에 있었는지 판단하거나 추정하지 않는다.

## 보호 범위

- 기존 `tasks/01-ralphthon/`부터 `tasks/04-tokenizer-comparison/`까지 수정하지 않는다.
- `_private/`, `_inbox/`, 기존 result와 ignored 파일을 읽거나 수정하지 않는다.
- 저장소 확산 실험은 임시 Git 저장소에서만 실행한다.
- 비밀값, API 키, 전체 홈 경로와 자격증명 위치를 산출물에 기록하지 않는다.
- 실험 도중 실패한 호출도 삭제하지 않고 상태와 종료 코드를 기록한다.

## 생성할 Task 05 구조

```text
tasks/05-ralphthon-spelling-evaluation/
├── EXECUTION_PLAN.md
├── README.md
├── AGENTS.md
├── CLAUDE.md
├── source/
│   ├── runner/
│   └── scorer/
├── data/
│   ├── cases.jsonl
│   ├── manifest.json
│   └── raw/
├── output/
│   ├── summary.csv
│   └── summary.json
└── docs/ralphthon-spelling-evaluation/
    ├── index.md
    └── results.md
```

`data/raw/`에는 비식별 처리된 원본 JSON 응답을 보존한다. Wiki 문서에는 OKF frontmatter의 `type`을 포함한다.

## 실행 환경 동결

실험 전에 다음 정보를 `data/manifest.json`에 기록한다.

- 모델 ID와 wrapper가 설정한 모델 환경
- `claude-upstage` 파일의 SHA-256
- Claude Code 버전
- `_Upstage` Git HEAD
- 시작 시각과 timezone
- 반복 횟수, randomization seed와 실제 case 실행 순서
- 실행 명령의 비밀정보가 제거된 형태

모든 probe는 새 세션으로 실행하고 `--no-session-persistence`를 사용한다. 자동 fallback 모델은 사용하지 않는다. 단순 언어 probe는 프로젝트 기억과 도구 영향을 줄이기 위해 `--bare --tools ""`를 적용한다.

## 실험 A — 철자 인식과 보존

다음 여섯 조건을 각각 독립 세션에서 10회 실행한다.

| case | 조건 | 핵심 입력 | 판정 |
| --- | --- | --- | --- |
| A1 | 명시적 복사 | 공식 철자가 `Ralphthon`이라고 명시 | exact match |
| A2 | 음차 추론 | “랄프톤의 영문 철자를 써라” | 생성 철자 분포, 오류 판정 금지 |
| A3 | 조어 구성 | `Ralph`와 `thon`을 결합한 신조어라고 설명 | `Ralphthon` 도출 여부 |
| A4 | 오타 교정 | `ralpthon`과 canonical `Ralphthon`을 함께 제공 | 교정 준수율 |
| A5 | 충돌 문맥 | 다수 오타와 하나의 authoritative glossary 제공 | glossary 준수율 |
| A6 | 지연 유지 | 처음 canonical 철자를 제시하고 중간 작업 뒤 다시 사용 | 최종 보존율 |

각 prompt에는 순서를 무작위화한 내부 대조 단어를 포함한다.

- 익숙한 단어: `hackathon`, `marathon`, `datathon`
- 유사 신조어: `Zalphthon`, `Morphton`
- 혼동 후보: `Ralpthon`, `Ralphathon`, `Ralph-thon`

정답이 명시된 조건에서는 모든 단어의 exact match를 비교한다. 신조어와 음차-only 항목은 입력에 canonical 철자가 없으면 설명 통계만 작성한다.

## 실험 B — 저장소 오류 확산

동일한 fixture로 격리된 임시 Git 저장소 10개를 생성한다. fixture에는 다음을 포함한다.

- `Ralphthon`과 `ralphthon`을 선언한 authoritative glossary
- 일부 문서에 의도적으로 삽입한 `ralpthon`
- task, Wiki, 실행 스크립트와 결과 폴더를 정리하라는 요구사항
- 현재 경로와 역사적 오류 인용을 구분하는 규칙

각 trial에서 Solar Open 2가 구조 정리와 참조 통일을 수행하게 한 뒤 다음을 측정한다.

- 잘못된 철자를 새로 생성했는지
- 오타가 확산된 파일과 경로 수
- 파일명, 폴더명, 본문, 코드 식별자 중 확산된 표면
- authoritative glossary 준수 여부
- 명시적 교정 뒤 잔존 오타와 재발 여부

임시 저장소의 절대 경로는 raw 결과에서 제거한다. trial 완료 뒤 `_Upstage`의 기존 파일 변경 여부를 검사한다.

## 실행기와 채점기

실행기는 `probe`, `agent`, `all`, `dry-run` 모드를 제공한다. 기본 반복 수는 10이며 case 순서를 seed 기반으로 무작위화한다.

채점기는 다음 결과를 CSV와 JSON으로 생성한다.

- exact match
- 대소문자 오류
- 삽입·삭제·치환과 Levenshtein distance
- 생성 철자별 빈도
- 경로와 본문별 확산 건수
- 조건별 성공 횟수와 Wilson 95% 신뢰구간

raw 응답을 수정하지 않고 별도 파생 결과만 생성한다. 동일 raw data를 다시 채점하면 byte-identical한 요약이 생성돼야 한다.

## 실행 순서

1. 보호 범위와 Git 상태를 기록한다.
2. Task 05 구조, case manifest, 실행기와 채점기를 만든다.
3. dry-run으로 철자 probe 60회와 저장소 trial 10회를 확인한다.
4. dry-run 결과와 예상 API 호출 수를 사용자에게 보고한다.
5. 사용자가 계속 실행하라고 하면 본 실험을 수행한다.
6. raw 결과를 비식별 처리하고 결정론적으로 채점한다.
7. `docs/ralphthon-spelling-evaluation/results.md`에 결과와 한계를 기록한다.
8. 기존 Task 01~04와 보호 대상에 변경이 없는지 검사한다.
9. `git diff --check`와 내부 링크 검사를 수행한다.
10. commit이나 push 없이 최종 상태와 변경 파일을 사용자에게 보고한다.

rate limit이나 호출 실패가 발생하면 자동 재시도로 목표 표본 수를 조용히 보충하지 않는다. 완료된 표본 수와 실패 이유를 `partial run`으로 보고하고 사용자 지시를 기다린다.

## 완료 기준

- 실제 응답이 모두 `solar-open2` 모델 실행으로 귀속된다.
- A1~A6은 조건별 10개의 독립 결과를 갖는다.
- 저장소 trial 10개가 서로 격리돼 있다.
- 음차 추론과 canonical 보존 오류가 별도 집계된다.
- raw 응답, manifest, 요약 결과와 보고서 사이의 case 수가 일치한다.
- 기존 Task 01~04와 보호 대상의 hash 또는 Git diff에 변화가 없다.
- 결과 보고서가 관찰, 해석, 한계와 provenance를 구분한다.

## 시작 명령

`_Upstage` 루트에서 다음과 같이 실행한다.

```bash
claude-upstage --model solar-open2
```

세션에 다음 지시를 전달한다.

```text
tasks/05-ralphthon-spelling-evaluation/EXECUTION_PLAN.md를 읽고 명세대로 Task 05를 수행해.
실험 대상의 canonical 철자는 Ralphthon이고 slug는 ralphthon이야.
기존 Task 01~04와 보호 대상은 수정하지 말고, commit이나 push도 하지 마.
먼저 preflight와 dry-run 결과를 보여준 뒤 명세의 실행 경계에 따라 진행해.
```
