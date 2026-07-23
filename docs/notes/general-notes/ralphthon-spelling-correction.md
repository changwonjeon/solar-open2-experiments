---
type: Log
title: "Ralphthon 표기 오류 정정 기록"
description: "Solar Open 2 작업 과정에서 Ralphthon을 잘못 표기한 문제의 범위, Git 근거와 canonical 경로 정정 내역"
tags: [solar-open2, ralphthon, naming, correction, agent-evaluation]
timestamp: 2026-07-23T00:00:00+09:00
---

# Ralphthon 표기 오류 정정 기록

## 결론

공식 표기는 **Ralphthon**이며 영문 경로와 식별자에는 `ralphthon`을 사용한다. 기존의 `ralpthon` 표기는 오타다.

Solar Open 2 기반 Claude Code 작업에서 이 오타가 한 문장에 그치지 않고 task, Wiki, 실행 스크립트, 로컬 Skill과 결과 폴더의 이름으로 반복 확산됐다. 사람이 정답 철자를 명시한 뒤 Codex가 예외적으로 작업 공간에 개입해 이름과 참조를 정정했다.

## Git 근거

| 근거 | 확인 내용 |
|---|---|
| `6d62228` | 2026-07-17 비교 실험 Wiki와 실행 스크립트 도입 시 잘못된 `src/scripts/ralpthon/` 경로가 사용됐다. |
| `7024b1b` | 2026-07-23 LLM-Wiki·OKF 구조 개편에서도 잘못된 철자가 유지됐다. |
| `e54b7a7` | task 작업 공간 통합 시 `tasks/01-ralpthon/`으로 오타가 canonical 경로에 확대됐다. |
| 정정 시작 기준 HEAD `41b686f` | 당시 `main`과 `origin/main`이 가리킨 커밋이다. |
| 정정 전 `git ls-files` | 잘못된 task 경로 아래에 tracked 경로 85개가 확인됐다. |

Git 이력은 과거 커밋 자체를 재작성하지 않고 보존한다. 현재 작업 트리와 향후 문서에서만 올바른 철자를 사용한다.

## 정정 범위

- `tasks/01-ralpthon/` → `tasks/01-ralphthon/`
- task Wiki의 `docs/ralpthon/` → `docs/ralphthon/`
- `src/scripts/ralpthon/` → `src/scripts/ralphthon/`
- `.claude/skills/run-ralpthon/` → `.claude/skills/run-ralphthon/`
- `src/data/results/ralpthon/` → `src/data/results/ralphthon/`
- Task 03 phase spec 파일명과 모든 현재 문서·스크립트 참조

`source/codex-original/`은 task 상위 경로 이동에 포함됐지만 내부 Ralphthon 코드의 올바른 package·Skill 이름은 보존했다. 오타가 있던 원본 보관 문서 2곳은 사용자의 전수 정정 지시에 따라 철자만 바로잡았다.

## 모델 평가상의 의미

이 사례는 Solar Open 2가 긴 작업에서 고유명사 철자를 한 번 잘못 정한 뒤, 그 표현을 여러 파일과 경로에 일관되게 복제할 수 있음을 보여준다. 구조화와 대량 수정 능력이 오히려 초기 명명 오류의 영향 범위를 넓힌 사례다.

이를 일반적인 코딩 능력 부족으로 확대해서 해석하지는 않는다. 다만 저장소 migration이나 canonical naming 작업에서는 다음 gate가 필요하다.

1. 작업 시작 전에 고유명사와 canonical 경로를 명시적인 사전으로 고정한다.
2. 이동 전후에 금지 문자열을 대소문자 구분 없이 전수 검색한다.
3. 파일명·폴더명과 본문 참조를 서로 다른 검사로 확인한다.
4. Git 이력에 등장하는 과거 경로와 현재 사용 경로를 구분해 기록한다.

## 검증 기준

일반 파일과 경로에서 `ralpthon` 검색 결과는 0건이어야 한다. 이 문서는 오류 증거를 보존하기 위해 잘못된 문자열을 의도적으로 인용하므로 검사 시 허용 문서로 분류한다.
