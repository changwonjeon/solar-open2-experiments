---
type: Ralph Context Snapshot
title: Ralphthon Track 2 Ralph Loop Context
description: 2026-07-12 12:30–15:30 자율 실행을 위한 동결 컨텍스트.
tags: [ralphthon, track-2, ralph, context, okf]
timestamp: 2026-07-12T12:15:45+09:00
---

# Task Statement

주최측 공식 Track 2-only 계약을 보존하면서 25분 안에 배정 논문 전체를 리뷰할 Codex Skill과 native multi-agent runtime을 만들고, 15:30까지 제출 가능한 익명 Technical Report PDF, Title, Abstract, Review Agent, 실행 증적, GitHub README, Human Editing handoff를 생성한다.

# Desired Outcome

- 프로젝트 로컬에서 발견되는 공식 `$auto-research` Skill과 wrapper `$ralphthon-track2-review-agent` Skill.
- Root Coordinator 1개와 persistent Review Worker 3개의 bounded runtime.
- mock 10편 3회, schema 100%, 중복 0건, timeout·restart·reconciliation 검증.
- 고정 gold fixture를 사용한 evidence-bound 방식과 naive single-pass baseline 비교.
- Tectonic으로 빌드한 익명 ICML 2026 Technical Report PDF, Title, Abstract.
- 15:30 `HANDOFF.md`와 16:35 live runbook.

# Known Facts and Evidence

- 행사 시간은 Ralph Loop 12:30–15:30, Human Editing 15:30–16:30, live review 16:35–17:00이다.
- 공식 upstream clone은 `tmp/ralphthon-icml-official`에 있고 commit은 `a9f4f2583648ef4ca54f980f951ae393d153473f`다.
- 공식 Track 2-only는 GPU, VESSL, W&B, 새 학습 실험이 필요하지 않다.
- OpenAgentReview 로그인은 완료됐지만 행사 venue는 아직 열리지 않았다.
- Git baseline은 private 원격 `changwonjeon/20260712-ralphthon-submit`의 `main`, commit `67a89a0ee7c18d6abdd4c5c734d5b1bdc97f8784`다.
- Codex CLI `0.144.1`, tmux `3.7b`, Tectonic `0.16.9`, Poppler, jq, Python 3가 준비됐다.
- Tectonic으로 공식 ICML 예제 TeX에서 7페이지 PDF 생성에 성공했다.
- browser, chrome, computer-use plugin은 설치·활성화되어 있지만 Safari 로그인 세션과 자동화 세션의 일치는 미검증이다.

# Constraints

- 사용자가 명시적으로 시작하기 전에는 Ralph Loop를 시작하지 않는다.
- 12:30 이후 사용자는 15:30까지 코딩 에이전트에 입력하지 않는다.
- credential, MFA, CAPTCHA, 실제 production claim/post, 유료 자원 생성은 Ralph 범위 밖이다.
- 15:20 feature freeze, 15:28 completion audit, 15:30 자동 쓰기 종료다.
- 확인되지 않은 API endpoint, selector, 실험 결과, citation을 발명하지 않는다.
- 익명 제출물에는 이름, 계정명, 로컬 경로, 개인 GitHub URL을 넣지 않는다.
- 모든 문서는 OKF v0.1 구조와 frontmatter를 따른다.

# Unknowns

- 행사 venue 공개 시각과 실제 assigned count.
- claim의 가역성, TTL, 복수 claim 가능 여부.
- PDF URL과 review form field의 실제 DOM/API 계약.
- 원격 제출 성공 표시와 receipt 형태.
- Safari 세션을 live Root가 직접 제어할 수 있는지 여부.

# Likely Touchpoints

- `.codex/skills/auto-research/`.
- `.codex/skills/ralphthon-track2-review-agent/`.
- `.codex/agents/`.
- `src/`, `tests/`, `fixtures/`, `evidence/`, `outbox/`.
- `submission/technical-report.tex`, `submission/technical-report.pdf`.
- `submission/TITLE.txt`, `submission/ABSTRACT.txt`.
- `README.md`, `RALPH_GOAL.md`, `CHECKPOINT.json`, `FAILURE_LEDGER.md`, `HANDOFF.md`.

# Source of Truth

1. 행사 당일 OpenAgentReview UI와 운영진 공지.
2. `.omx/plans/ralphthon-track2-skill-creation-plan.md`.
3. `guides/20260712_Track-2-Participant-Guide.md`.
4. 공식 upstream commit `a9f4f2583648ef4ca54f980f951ae393d153473f`.

