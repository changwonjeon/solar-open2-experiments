---
type: Ralph Goal
title: Ralphthon Track 2 Autonomous Build Goal
description: 12:30–15:30 Ralph Loop가 질문 없이 실행할 동결 목표와 검증 계약.
tags: [ralphthon, track-2, ralph, codex, okf]
timestamp: 2026-07-12T12:15:45+09:00
status: frozen-pending-user-start
---

# Ralph Goal

15:30 KST까지 주최측 공식 `auto-research` Track 2-only 계약을 보존하면서, 배정 논문 전체를 25분 안에 처리할 Codex Skill과 native multi-agent runtime을 구현하라. mock 10편 반복시험, schema·품질·중복·timeout·재시작 검증을 통과시키고, 익명 Technical Report 소스와 PDF, Title, Abstract, `review-agent.md`, root `README.md`, 실행 증적, `HANDOFF.md`를 생성하라.

# Required Intake

작업을 시작하기 전에 다음 파일을 전부 읽는다.

- `.omx/context/ralphthon-track2-20260712T031545Z.md`.
- `.omx/plans/ralphthon-track2-skill-creation-plan.md`.
- `guides/20260712_Track-2-Participant-Guide.md`.
- `deliverables/ralphthon_track2_codex_package/docs/submission_contract.md`.
- `tmp/ralphthon-icml-official/skills/auto-research/SKILL.md`.

공식 upstream commit은 `a9f4f2583648ef4ca54f980f951ae393d153473f`이며 Git baseline은 `67a89a0ee7c18d6abdd4c5c734d5b1bdc97f8784`다.

# Autonomy Contract

- 사용자에게 질문하지 않는다. `omx question`을 실행하지 않는다.
- credential, MFA, CAPTCHA, 실제 production claim/post, 유료 자원을 요구하지 않는다.
- 확인되지 않은 OpenAgentReview endpoint와 selector를 발명하지 않는다.
- 외부 플랫폼이 막혀도 mock adapter, fixtures, validation, report, runbook 작업을 계속한다.
- 같은 failure signature가 두 번 반복되면 `FAILURE_LEDGER.md`에 기록하고 축소 경로로 전환한다.
- 각 P0 gate 뒤 `CHECKPOINT.json`을 갱신한다.
- 원격 Git push는 하지 않는다. 로컬 commit은 검증 checkpoint 용도로 허용한다.
- VESSL, GPU, W&B, 새 학습 실험은 수행하지 않는다.

# P0 Deliverables

- `.codex/skills/auto-research/`에 upstream subtree를 원본 그대로 설치하고 hash를 검증한다.
- `.codex/skills/ralphthon-track2-review-agent/`에 wrapper Skill, references, assets, validators를 만든다.
- `.codex/agents/`에 live Review Worker와 build verifier/auditor를 만든다.
- canonical schema는 upstream `Contribution`과 행사 `Significance`, `Originality`, `Comment`를 모두 보존하며 임의 환산하지 않는다.
- 각 논문은 Worker 실행 전에 input/evidence hash를 per-paper manifest로 동결한다.
- Root만 claim, post, status, ledger를 소유하고 Worker 3개는 `ReviewDraft`만 반환한다.
- mock adapter, bounded queue, lease, atomic ledger, idempotency, claim/post status-first reconciliation을 구현한다.
- gold fixture를 agent 실행 전에 동결하고 naive single-pass baseline, TP/FP/FN, location-match 규칙, threshold를 기록한다.
- `submission/technical-report.tex`와 `submission/technical-report.pdf`를 공식 ICML 2026 style로 만든다.
- `submission/TITLE.txt`, `submission/ABSTRACT.txt`, `review-agent.md`, `README.md`, `MANUAL_PLATFORM.md`, `HANDOFF.md`를 만든다.
- `outbox/<paper_id>.json`과 clipboard-ready text fallback을 만든다.

# Absolute Time Gates

- 12:30–12:45. 공식 Skill 설치, contract, report skeleton, gold fixture, baseline을 동결한다.
- 12:45–13:25. 최소 Skill, schema, Root/Worker, mock adapter를 구현하고 1편 end-to-end를 통과한다.
- 13:25–14:05. 10편 worker pool, validator, ledger, timeout 복구를 구현한다.
- 14:05–14:35. failure injection, restart, duplicate 방지와 2차 검증을 수행한다.
- 14:35–15:00. 10편 3회와 seeded 품질 평가를 완료하고 report evidence table을 갱신한다.
- 15:00–15:20. PDF, Title, Abstract, review-agent, README, manifest, runbook을 최종화한다.
- 15:20. 신규 기능을 금지한다.
- 15:20–15:28. architect 검증, changed-files-only deslop, 전체 회귀검사, 익명성·페이지·placeholder 검사를 수행한다.
- 15:28. Ralph completion state와 `HANDOFF.md`를 완성한다.
- 15:30. 자동 쓰기를 종료한다.

# Validation Gates

- 공식 `$auto-research`와 wrapper `$ralphthon-track2-review-agent`를 새 Codex 세션에서 각각 발견한다.
- mock 10편을 3회 실행해 assigned count 전체 완료, schema 100%, duplicate 0건을 확인한다.
- malformed JSON, Worker timeout, claim timeout, post timeout, process restart를 주입한다.
- `quick_validate.py`, unit tests, integration tests, lint/static checks를 실행한다.
- Tectonic으로 PDF를 빌드하고 `pdfinfo`로 페이지를 확인한다.
- `pdftotext`와 metadata 검사로 이름, `changwonjeon`, `redux80`, `/Users/`, 이메일, 개인 GitHub URL, author/acknowledgment, placeholder를 hard fail한다.
- 본문 종료 marker가 4페이지 이내인지 확인한다.
- Title, Abstract, report의 수치가 raw evidence와 일치하지 않으면 실패한다.
- explicit architect 검증을 통과한다.
- 변경 파일만 ai-slop-cleaner로 정리한 뒤 전체 회귀검사를 다시 통과한다.
- Ralph state에 prompt-to-artifact checklist와 fresh verification evidence를 기록하고 read-back한다.

# Live Design Contract

- 성공 조건은 `posted_verified == assigned_count`다.
- 16:35부터 최대 45초 `LIVE_DISCOVERY`로 실제 assigned count와 UI 계약을 확인한다.
- Platform Lane 우선순위는 `reconcile/post > download > claim > browse`다.
- 기본 queue high-water는 3이며 복수 claim 허용 확인 뒤에만 6으로 올린다.
- 자동 브라우저 실패 시 `MANUAL_PLATFORM.md`로 전환하되 reviewer와 outbox 생성은 계속한다.
- 생산 환경 claim/post는 Ralph Loop 중 실행하지 않는다.

# Required Handoff

`HANDOFF.md`에는 P0별 pass/fail, 변경 파일, Skill 호출법, 마지막 테스트 출력, 실제 측정값, 실패와 한계, PDF·Title·Abstract·review-agent·README 경로, 16:35 live 명령, manual fallback, 아직 사람이 확인할 항목을 기록한다. 계획이나 mock을 실제 플랫폼 성능으로 표현하지 않는다.

# Stop Condition

모든 P0가 검증되었거나 15:20 freeze가 시작되면 구현을 중단한다. 실패가 남아도 제출자료와 handoff를 정직하게 완성한다. 15:30 이후 파일을 수정하지 않는다.

# Operator Boundary

이 Goal과 launcher가 준비되어 있어도 사용자의 명시적인 시작 신호 전에는 실행하지 않는다. 실제 시작은 행사 진행에 맞춰 사용자가 지시한다.

사용자 시작 신호 뒤 실행할 유일한 명령은 프로젝트 루트에서 `./work/start-ralph-loop.sh START-RALPH`다. bare `omx ralph`는 Goal, keep-awake, 고정 tmux session, deadline watcher를 함께 보장하지 않으므로 사용하지 않는다.
