---
type: Execution Specification
title: Ralphthon Track 2 전체 실행 계획과 Ralph Loop 명세
description: 오전 사전 설정부터 3시간 무인 Ralph Loop, Human Editing, 최종 제출, 25분 리뷰 실행까지 포괄하는 분산형 Codex Skill 제작 명세.
tags: [ralphthon, track-2, codex, skill, multi-agent, okf]
timestamp: 2026-07-12T11:40:00+09:00
status: preflight-in-progress
---

```text
오전 준비 단계. SPEC / PREFLIGHT. 11:56–12:30

  공식 auto-research Skill + 행사 가이드와 제출 규정
             |
             v
  [계약 동결]--->[실행 명세·입력·계정 사전 점검]--->[Ralph Goal 동결]
       |                       |                         |
       +--> 제출 계약          +--> 무인 복구 규칙        +--> 12:30 Launch

오후 제작 단계. RALPH LOOP. 12:30–15:30

  [Frozen Goal + Spec]
           |
           v
  공식 Skill 고정 -> Skill 확장 구현 -> Test / Repair Loop -> Mock 10편
           |                |                 |               |
           +----------------+-----------------+---------------+
                                    |
                                    v
                    Skill + Report + Evidence + Handoff 동결

사람 편집과 제출. 15:30–16:30

  자동 산출물 -> 사람 검토·익명화·4페이지 확인 -> PDF·Title·Abstract 제출

실전 리뷰 단계. LIVE. 16:35–17:00

  OpenAgentReview
        |
        v
  [Root Coordinator / Deadline Controller]
        |  claim·queue·lease·ledger·validate·post·receipt를 단일 소유.
        |
        +--------+----------------+----------------+
        |        |                |                |
        v        v                v                v
   Worker A  Worker B        Worker C       직렬 Platform Lane
     PDF       PDF              PDF          claim / post / status
      |         |                |
      +---------+----------------+
                |
                v
        ReviewDraft JSON
                |
                v
      [결정론적 Schema Validator]
          | 통과            | 실패
          v                 v
       post + receipt    1회 targeted repair
          |                 |
          +--------+--------+
                   v
          10/10 최종 상태 감사
```

# 1. 목표

행사 당일 Track 2의 실제 성공 조건은 16:35–17:00의 25분 동안 배정 논문 10편을 모두 리뷰하고 OpenAgentReview 제출 상태를 확인하는 것이다. 제작할 Skill은 주최측의 공식 `auto-research` Skill과 Track 2 템플릿을 upstream 기준으로 사용하고, 이 위에 10편 병렬 처리와 제출 복구 계층을 추가한다. 익명 Technical Report PDF, Title, Abstract와 재현 가능한 실행 증적도 함께 준비한다.

이 문서는 오전 Research Specification, 오후 Ralph Loop, Human Editing, 최종 제출, 실제 리뷰까지 이어지는 전체 실행 명세다. 오전 계획 단계에서는 `.codex/skills` 또는 `.codex/agents` 파일을 생성하지 않고, 12:30에 동결된 Goal과 이 명세를 Ralph Loop에 전달해 구현을 시작한다.

# 2. 전체 시간표와 단계별 종료 조건

| 시간 | 단계 | 자동화 주체 | 종료 조건 |
| --- | --- | --- | --- |
| 11:56–12:20 | Spec 확정과 preflight. | 사람 + 현재 Codex 세션. | 입력·공식 upstream·실행 Goal·계정 경계·복구 규칙이 동결됨. |
| 12:20–12:27 | Launch rehearsal. | 현재 Codex 세션. | context snapshot, 명령, 작업경로, writable path, mock 입력, 로그 위치를 확인함. |
| 12:27–12:30 | 최종 freeze와 Ralph 시작. | 사람. | Goal을 한 번 입력하고 이후 개입 없이 실행 가능함. |
| 12:30–15:30 | Ralph Loop 자율 제작. | Ralph leader + native subagents. | Skill, agents, tests, mock 결과, 보고서 초안, handoff가 생성·검증됨. |
| 15:30–16:20 | Human Editing. | 사람 + 필요 시 Codex. | 익명 PDF, Title, Abstract가 최종 검토되고 업로드됨. |
| 16:20–16:30 | 제출 여유와 receipt 확인. | 사람. | 16:30 전에 제출 성공 상태와 로컬 사본이 확인됨. |
| 16:30–16:35 | 매칭 대기와 live preflight. | 사람 + Root. | 로그인·세션·실행 명령·빈 원장을 확인함. |
| 16:35–17:00 | 실제 Review Agent 실행. | Root + Worker 3개. | 배정된 전체 논문의 review와 원격 제출 상태가 확인됨. |

12:30 Ralph Loop의 종료점은 코드를 많이 만드는 것이 아니다. `검증된 Skill + 제출 가능한 자료 + 15:30 사람이 바로 판단할 handoff`를 남기는 것이 종료점이다.

Ralph Loop의 실제 시작 권한은 사용자에게만 있다. Codex는 사용자가 행사 진행에 맞춰 명시적으로 시작하라고 말하기 전에는 `omx ralph`, caffeinate keeper, watchdog을 실행하지 않는다. 오전에는 시작 명령과 모든 입력만 준비한다.

# 3. 설계 원칙

- 주최측 공식 저장소의 `auto-research` Skill을 복제·재작성하지 않고, 버전과 commit을 고정한 upstream 계약으로 사용한다.
- 공식 Track 2-only 경로의 `review-agent.md`, frozen paper hash, evidence trace, ICML-style review 계약을 보존한다.
- 라이브 동시성은 Root Coordinator 1개와 Review Worker 3개로 제한한다.
- Root만 플랫폼의 claim, post, status 확인과 원장을 변경한다.
- Worker는 논문을 읽고 구조화된 `ReviewDraft`만 반환한다.
- 논문마다 Critic, Verifier, Judge를 별도 실행하지 않는다. 10편에 30회 이상의 에이전트 실행이 필요해 시간 제한을 초과할 위험이 크다.
- Critic–Verifier 사고법은 Worker 내부 체크리스트로 유지하고, 형식 검증은 결정론적 validator가 담당한다.
- 브라우저/API의 병렬 안전성이 입증되기 전까지 claim과 post는 직렬화한다.
- 게시 timeout은 즉시 재시도하지 않고 status를 먼저 조회한다. 결과가 불명확하면 `post_unknown`으로 기록하고 대조한다.
- 한 논문의 실패가 전체 batch를 중단시키지 않도록 timeout, 재큐잉, 영수증을 논문 단위로 관리한다.

# 4. 범위

## 포함 범위

- Codex Skill의 호출 계약과 `BUILD`, `DRY-RUN`, `LIVE` 모드.
- Root Coordinator와 Review Worker용 native agent 설계.
- 리뷰 출력 JSON schema와 필수 점수 범위 검증.
- 논문 입력, Skill 버전, prompt hash, 리뷰 결과, 게시 영수증의 provenance.
- 10편 mock 처리량 시험과 timeout·중복·재시작 시험.
- Technical Report, Title, Abstract 작성 및 익명성·분량 검사.
- 최종 산출물 동결과 제출 전 감사.

## 제외 범위

- 실제 행사 플랫폼의 확인되지 않은 API endpoint 추정.
- 논문당 다단계 토론형 에이전트 체인.
- 새로운 외부 의존성 도입.
- 사용자 승인 전 Skill 및 native agent의 실제 생성.
- Track 2-only와 무관한 VESSL GPU, W&B, 새 학습 실험 구성.

# 5. 예정 파일 구조

```text
.codex/
├── skills/
│   └── ralphthon-track2-review-agent/
│       ├── SKILL.md
│       ├── agents/
│       │   └── openai.yaml
│       ├── references/
│       │   ├── review-contract.md
│       │   ├── runtime-runbook.md
│       │   └── submission-contract.md
│       ├── assets/
│       │   ├── review-agent-template.md
│       │   ├── review-output-template.json
│       │   └── technical-report-outline.md
│       └── scripts/
│           ├── validate_review.py
│           ├── hash_inputs.py
│           └── audit_receipts.py
├── RALPH_GOAL.md
├── README.md
├── FAILURE_LEDGER.md
├── CHECKPOINT.json
├── HANDOFF.md
├── .omx/context/ralphthon-track2-<timestamp>.md
└── agents/
    ├── track2-review-worker.toml
    ├── track2-review-verifier.toml
    └── track2-submission-auditor.toml
```

`track2-review-verifier`와 `track2-submission-auditor`는 구축·리허설·최종 감사용이다. 라이브 논문 처리 슬롯은 Coordinator와 Worker 3개만 사용한다. Skill 폴더에는 불필요한 README, 설치 안내, 변경 이력을 추가하지 않는다.

# 6. 실행 모드

| 모드 | 목적 | 외부 부작용 |
| --- | --- | --- |
| `BUILD` | 계약, prompt, schema, validator, 제출 문서 생성과 검증. | 없음. |
| `DRY-RUN` | mock 논문 10편으로 병렬 처리량, 실패 격리, 재시작 검증. | 없음. |
| `LIVE` | 실제 논문 claim, 리뷰, 검증, 게시, 상태 감사. | Root만 허용. |

# 7. 역할 계약

## Root Coordinator

- deadline과 stop condition을 관리한다.
- 플랫폼 login과 실제 UI/API를 확인한 뒤 adapter 계약을 동결한다.
- 논문을 claim하고 작업 queue와 lease를 관리한다.
- Worker 3개에 독립 작업을 배정한다.
- validator 통과 결과만 게시한다.
- 게시 전후 상태와 receipt를 원장에 기록한다.
- 23분부터 신규 작업을 중단하고 상태 감사에 집중하며, 24분에는 hard stop을 적용한다.

## Review Worker

- 한 번에 논문 한 편만 처리한다.
- PDF 또는 추출 텍스트에서 주장, 방법, 실험, 한계의 근거를 찾는다.
- 필수 점수, 짧은 근거, evidence trace, questions, ethics/limitations를 포함한 `ReviewDraft`를 반환한다.
- claim, post, status 조회, 공유 원장 수정은 하지 않는다.
- timeout 또는 parse 실패 시 오류를 구조화해 반환하며 자체 무한 재시도를 하지 않는다.

## 결정론적 Validator

- 필수 필드 누락과 점수 범위를 검사한다.
- 빈 comment, 근거 없는 점수, placeholder를 거부한다.
- paper ID와 lease ID의 일치를 검사한다.
- 실패 시 한 차례의 targeted repair 입력만 생성한다.

# 8. 리뷰 출력 계약

필수 행사용 필드는 다음과 같다.

- `soundness`: 1–4.
- `presentation`: 1–4.
- `significance`: 1–4.
- `originality`: 1–4.
- `overall_recommendation`: 1–6.
- `confidence`: 1–5.
- `comment`: 비어 있지 않은 ICML-style 종합 의견.

내부 감사 필드는 `paper_id`, `summary`, `strengths`, `weaknesses`, `questions`, `ethics_and_limitations`, `evidence_trace`, `score_rationales`, `worker_id`, `prompt_hash`, `input_hash`, `started_at`, `completed_at`으로 계획한다. 실제 플랫폼이 받지 않는 내부 필드는 게시 adapter가 제거하되 로컬 증적에는 보존한다.

# 9. 시간 예산과 상태 모델

논문당 평균 허용 시간은 150초다. Worker 3개가 병렬로 초안을 생성하고 Root가 검증과 게시를 직렬 처리한다.

```text
discovered -> claiming -> claimed -> downloaded -> leased -> drafted -> validated
                  \-> claim_unknown
                                                        |
                                                        v
                                                     posting
                                                   /         \
                                             posted       post_unknown
                                                             |
                                                             v
                                                    status reconciliation
```

- Worker timeout은 한 번만 재큐잉하고 batch는 계속한다.
- 동일 paper ID에는 활성 lease를 하나만 허용한다.
- `posting`에서 timeout이 발생하면 게시 재시도 전에 원격 status를 조회한다.
- 23분 시점에는 `posted`, `post_unknown`, 미완료 목록을 대조한다.
- claim timeout도 post timeout처럼 원격 상태를 먼저 대조하며 동일 논문 중복 claim을 금지한다.
- 성공 조건은 `posted_verified == assigned_count`다. 실제 배정 수가 10일 때 10/10으로 보고한다.
- Platform Lane 우선순위는 `reconcile/post > download > claim > browse`다.
- 기본 queue high-water는 3이며, 복수 claim이 허용됨을 확인한 뒤에만 6으로 올린다.

# 10. 오전 12:30 전 사전 설정 체크

## 자동 점검으로 확인된 항목

- Codex CLI `0.144.1`이 설치되어 있다.
- OMX doctor는 15개 항목 통과, 3개 warning, 실패 0개다.
- Python 3, Ruby, `jq`, Git, `pdftotext`, `pdfinfo`가 설치되어 있다.
- 공식 저장소가 `tmp/ralphthon-icml-official`에 있으며 현재 commit은 `a9f4f2583648ef4ca54f980f951ae393d153473f`다.
- ICML 2026 LaTeX style과 예제 PDF가 `attachments/icml2026/`에 있다.
- 제출 계약, Technical Report outline, Title·Abstract 초안, Review Agent 템플릿이 작업 패키지에 있다.
- 작업 폴더는 Git 저장소이며 private 원격 `changwonjeon/20260712-ralphthon-submit`의 `main`에 baseline commit `67a89a0ee7c18d6abdd4c5c734d5b1bdc97f8784`가 push되어 있다.
- `tmux 3.7b` 설치를 완료했고 임시 detached session에서 Codex CLI와 OMX doctor가 정상 실행되는 것을 확인했다. 12:30 실행 표면은 OMX `omx ralph`로 확정한다.
- GitHub CLI는 `changwonjeon` 계정으로 인증되어 있고 baseline push를 완료했다. Ralph 중에는 원격 push를 요구하지 않는다.
- Tectonic `0.16.9`를 설치했고 공식 ICML 예제 `.tex`에서 7페이지 PDF를 생성했다. Ralph는 같은 경로로 Technical Report를 빌드하고 `pdfinfo`·`pdftotext`로 검증한다.
- mock 품질 평가에 사용할 서로 다른 논문은 아직 10편이 없다. 처리량 fixture 10개와 품질용 seeded cases를 Ralph의 P0 입력으로 생성해야 한다.

## 사람이 12:30 전에 반드시 확인할 항목

- [x] OpenAgentReview에 로그인하고 기본 세션을 확인했다. 행사 venue는 아직 열리지 않았다.
- [x] 현재 로그인에 필요한 인증 절차를 완료했다.
- [x] 행사 Discord와 Luma의 최신 공지에 이상이 없음을 확인했다.
- [x] 네트워크, AC 전원 연결, 약 45GiB의 여유 디스크를 확인했다.
- [ ] Ralph Loop를 실행할 tmux pane과 작업 폴더를 확정한다.
- [x] `tmux 3.7b`를 설치하고 detached session에서 Codex·OMX smoke test를 통과했다.
- [x] GitHub 인증과 private 원격 push를 확인했다.
- [ ] Ralph 시작 직전 `git status`가 clean이고 baseline tag 또는 commit이 있는지 확인한다.
- [x] private 원격에 baseline commit `67a89a0ee7c18d6abdd4c5c734d5b1bdc97f8784`를 push했다.
- [ ] Ralph Goal, 이 plan 경로, 공식 upstream commit, 15:30 hard stop을 launch prompt에 포함한다.
- [ ] 노트북을 만질 수 없는 12:30–15:30 동안 credential prompt나 확인 대화가 발생하지 않도록 외부 계정 작업을 Ralph 범위에서 제외한다.
- [x] 전원을 연결했다. 실제 Ralph 시작 신호 뒤에만 `/usr/bin/caffeinate -dimsu` keeper를 시작한다.

## 현재 OMX warning의 처리

- Explore Harness와 deprecated explore routing warning은 Ralph Loop의 구현·테스트에 필수 blocker가 아니다. 일반 native subagent와 shell 검증을 사용한다.
- Spark model 설정이 stale하므로 속도 예측에 영향을 줄 수 있다. 12:20 이전에 안전하게 검증할 시간이 있을 때만 `omx setup --force`를 수행하며, 그렇지 않으면 현재 정상 동작하는 standard 역할을 사용한다.
- 설정 변경 후 launch rehearsal을 다시 통과하지 못하면 기존 설정으로 Ralph를 실행한다.

# 11. Ralph Loop 3시간 실행 명세

## Frozen Goal

> 15:30까지 주최측 공식 `auto-research` Track 2-only 계약을 보존하면서, 배정 논문 10편을 25분 안에 처리할 Codex Skill과 native multi-agent runtime을 구현하라. mock 10편 반복시험, schema·중복·timeout·재시작 검증을 통과시키고, 익명 Technical Report 소스·PDF 초안·Title·Abstract·review-agent.md·실행 증적·15:30 handoff를 생성하라. OpenAgentReview의 확인되지 않은 API나 selector를 발명하지 말고, credential 또는 실제 게시가 필요하면 mock adapter로 계속 진행하면서 blocker와 15:30 인간 작업을 명시하라. 15:20부터 신규 기능을 금지하고 15:30에 검증된 산출물을 동결하라.

## Ralph 내부 반복 계약

```text
inspect -> select highest-priority unmet acceptance criterion
        -> implement smallest complete slice
        -> run targeted validation
        -> record evidence and remaining risk
        -> repair on failure
        -> continue until all P0 gates pass or 15:20 freeze begins
```

- Ralph leader가 backlog, 시간, shared files, 최종 통합을 소유한다.
- 독립 작업은 `executor`, `test-engineer`, `writer`, `verifier` native subagent에 병렬 배정한다.
- 같은 파일을 여러 agent가 동시에 수정하지 않는다.
- 매 반복은 코드 또는 문서 변경, 검증 출력, 다음 미충족 기준 중 하나를 남겨야 한다.
- 한 iteration은 최대 20분으로 제한하며, 같은 failure signature가 두 번 반복되면 `FAILURE_LEDGER.md`에 기록하고 축소 경로로 전환한다.
- 각 P0 gate 완료 시 `CHECKPOINT.json`을 원자적으로 갱신해 프로세스 재시작 시 마지막 완료 gate부터 이어간다.
- blocker가 생겨도 mock adapter, fixture, 문서화처럼 독립적으로 진행 가능한 작업은 계속한다.
- credential, CAPTCHA, 실제 외부 게시, 유료 자원 생성은 시도하지 않는다.
- 15:20 이후 신규 기능을 중단하고 회귀검사, PDF 생성, manifest, handoff만 수행한다.
- 15:28에 마지막 검증 결과를 기록하고 15:30에는 프로세스가 종료 가능한 상태여야 한다.
- 모든 acceptance criterion을 일찍 달성하면 추가 기능보다 새 세션 검증, failure injection, PDF 품질, handoff 개선 순서로 남은 시간을 사용한다.
- 최종 완료 전 explicit `architect` native subagent 검증을 반드시 통과한다.
- architect 승인 뒤 Ralph가 변경한 파일만 `ai-slop-cleaner`로 정리하고 전체 회귀검사를 다시 통과한다.
- 완료 audit을 Ralph state에 기록하고 read-back으로 checklist와 verification evidence를 확인한 뒤 종료한다.

## Ralph 우선순위 backlog

1. P0. 공식 upstream과 행사 제출 계약 동결.
2. P0. gold가 사전 동결된 10개 paper ID 처리량 fixture와 근거가 심어진 quality cases 준비.
3. P0. Skill skeleton, ReviewDraft schema, Root/Worker 권한 경계.
4. P0. mock adapter와 10편 bounded worker pool.
5. P0. validator, ledger, idempotency, timeout·status reconciliation.
6. P0. 10편 3회, 중복 0건, schema 100%, restart 시험.
7. P0. `review-agent.md`, Technical Report source/PDF 초안, Title, Abstract, manifest.
8. P0. GitHub 루트 `README.md` 작성과 최종 검증 결과 반영.
9. P0. seeded quality cases와 evidence trace 평가. 고정 baseline, TP/FP/FN, location-match 규칙과 threshold를 먼저 동결한다.
10. P1. 새 세션 Skill load와 launch smoke test.
11. P2. 성능·표현 개선. 모든 P0가 통과한 뒤에만 수행한다.

## 무인 복구와 stop condition

- 테스트 실패는 최대 두 번의 원인별 repair 뒤 해당 기능을 축소한다.
- 플랫폼 adapter가 불명확하면 mock adapter를 source of truth로 유지하고 live adapter blocker를 handoff한다.
- PDF 빌드가 실패하면 즉시 Tectonic 빌드 경로를 repair한다. 15:20에도 PDF가 없으면 submission package 실패로 표시하고 source와 로그를 handoff한다.
- native subagent가 실패하면 Worker 3→2→1 순으로 축소하고, 최종적으로 단일 프로세스 bounded queue로 전환한다.
- PDF 텍스트 추출이 실패하면 페이지 이미지와 vision 입력으로 전환한다.
- 네트워크가 끊기면 로컬 구현·mock·보고서 작업을 계속하고 외부 확인을 handoff에 남긴다.
- 14:50까지 10편 1회가 통과하지 못하면 품질 실험을 중단하고 처리량·제출 안정화만 수행한다.
- 15:10까지 10편 3회가 통과하지 못하면 성공한 반복 수와 실패 원인을 정직하게 보고하고 산출물 생성으로 전환한다.
- 15:20은 무조건 feature freeze다.

## 15:30 handoff 필수 내용

- P0 acceptance criterion별 통과·실패 표.
- 변경 파일과 Skill 호출 방법.
- 테스트 명령과 마지막 실제 출력.
- mock 10편의 완료 시간, 성공 수, 중복 수, schema 통과율.
- 알려진 blocker와 사람이 해야 할 작업을 우선순위·예상시간과 함께 기록.
- Technical Report source/PDF, Title, Abstract, `review-agent.md`, hash manifest 경로.
- GitHub 루트 `README.md`와 재현 가능한 setup·run·test 명령.
- 16:35 live 실행 명령과 emergency fallback 절차.
- 15:30 이후 Ralph가 산출물을 수정하지 않도록 종료되었다는 확인.

## Launch artifact와 실제 시작 표면

12:20까지 Ralph 지침이 요구하는 context snapshot을 `.omx/context/ralphthon-track2-<UTC timestamp>.md`에 만들고, task statement, desired outcome, known evidence, constraints, unknowns, touchpoints를 기록한다. 위 Frozen Goal은 별도 `RALPH_GOAL.md`로 복사하고 plan 절대경로, snapshot 경로, upstream commit, baseline commit, 절대 마감, 검증 명령, `HANDOFF.md` 경로를 포함해 hash로 동결한다.

실행 표면은 설치·smoke test가 끝난 OMX `omx ralph`로 확정한다. Codex는 `workspace-write` sandbox와 `approval=never`를 사용해 workspace 밖의 위험한 동작은 막으면서 승인 대기로 멈추지 않게 한다. 별도 `caffeinate` keeper를 3시간 이상 실행하고 Ralph를 시작한다. 정확한 명령과 PID·tmux session 확인 절차는 `RALPH_GOAL.md`에 기록한다.

12:27 launch rehearsal이 실패하면 native Codex goal/subagent 경로를 fallback으로 사용하되 동일한 `RALPH_GOAL.md`, checkpoint, deadline gate를 유지한다. 두 경로 모두 실패하면 No-Go다.

# 12. Ralph Loop 내부 예상 시간 배분

| 시간 | 작업 | 완료 증거 |
| --- | --- | --- |
| 12:30–12:45 | upstream 설치, spec, report skeleton, baseline, gold fixture 동결. | contract, report source, baseline test가 존재함. |
| 12:45–13:25 | Skill, schema, Root/Worker, mock adapter 구현. | 최소 end-to-end 1편이 통과함. |
| 13:25–14:05 | worker pool, ledger, validator, timeout 복구 구현. | mock 10편 1회가 완료됨. |
| 14:05–14:35 | failure injection, restart, idempotency 검증과 repair. | 중복 0건과 복구 증적이 존재함. |
| 14:35–15:00 | mock 10편 반복시험과 seeded quality 평가. | 처리량·품질 측정표가 생성됨. |
| 15:00–15:20 | 누적 evidence로 Technical Report, Title, Abstract, review-agent, README, manifest 최종화. | 제출자료 초안이 모두 존재함. |
| 15:20–15:30 | feature freeze, 최종 회귀검사, handoff. | 사람이 즉시 검토할 handoff가 완성됨. |

# 13. 구현 순서

1. 주최측 공식 저장소의 현재 commit과 `auto-research` Skill, Track 2 assets를 upstream으로 동결한다.
2. 공식 `auto-research` subtree를 commit `a9f4f2583648ef4ca54f980f951ae393d153473f` 기준으로 project-local `.codex/skills/auto-research/`에 설치하고 원본 hash를 검증한다.
3. 행사 가이드에서 리뷰 필드, 점수 범위, 제출물, 시간 제한을 `submission-contract.md`로 동결한다.
4. 공식 `review-agent.md` 계약을 유지하면서 upstream의 `Contribution`과 행사 UI의 `Significance`, `Originality`, `Comment`를 모두 보존하는 canonical `ReviewDraft` schema를 정의한다. 임의 환산은 금지한다.
5. 각 논문은 다운로드 직후 input hash와 evidence path를 per-paper run manifest로 동결한 뒤 Worker에 전달한다.
6. gold fixture, naive single-pass baseline, TP/FP/FN·location match 규칙과 threshold를 먼저 동결한다.
7. 실제 OpenAgentReview 화면을 읽기 전에는 adapter를 추정하지 않고 `UNKNOWN`으로 남긴다.
8. 결정론적 validator와 provenance script를 작성하고 단위 검증한다.
9. Root와 Worker의 권한 경계를 prompt와 native agent 설정에 중복 명시한다.
10. `BUILD`와 `DRY-RUN`에서 외부 게시 동작이 불가능하도록 guard를 둔다.
11. mock 10편으로 처리량, 품질, 실패 격리를 검증한다.
12. Technical Report skeleton을 초기에 만들고 측정값이 생길 때마다 evidence table을 갱신한다.
13. Technical Report, Title, Abstract를 실제 실행 증적과 일치시키고 익명성·4페이지 제한을 검사한다.
14. Skill과 산출물을 hash로 동결하고 라이브 실행 runbook을 확정한다.

# 14. 검증 계획

## 정적 검증

- Skill frontmatter, 이름, description, 링크를 `quick_validate.py`로 검사한다.
- 모든 JSON fixture를 schema validator로 검사한다.
- native agent 파일의 role, tool 권한, prompt 경로를 검사한다.
- 최종 문서의 placeholder, 실명·소속, 페이지 제한을 검사한다.
- `pdftotext`, `pdfinfo`로 `Changwon`, `Jeon`, `changwonjeon`, `redux80`, `/Users/`, 이메일, 개인 GitHub URL, author/acknowledgment, placeholder를 hard fail한다.
- PDF metadata의 Author가 비어 있거나 Anonymous인지 확인하고, 본문 종료 marker가 4페이지 이내인지 확인한다.
- 새 세션에서 공식 `$auto-research`와 wrapper `$ralphthon-track2-review-agent`가 각각 발견되는지 확인한다.

## 동작 검증

- 새 Codex 세션에서 `$ralphthon-track2-review-agent`가 필요한 reference만 점진적으로 로드하는지 확인한다.
- mock 10편을 Worker 3개로 실행해 10/10 완료, 중복 0건, 필드 완전성 100%를 확인한다.
- Worker timeout, malformed JSON, validator reject, post timeout을 각각 주입한다.
- 중단 후 원장에서 재시작했을 때 이미 게시된 논문을 다시 게시하지 않는지 확인한다.
- 가능할 때 실제 플랫폼 논문 1편으로 claim→read→review→post→status의 왕복을 검증한다.
- 16:35 전 production에서는 claim과 test post를 하지 않는다. read-only login/browse/PDF smoke test만 수행하며, 주최측이 명시한 sandbox가 있을 때만 claim→post 왕복을 검증한다.
- explicit architect 검증, changed-files-only deslop, post-deslop regression을 통과한다.
- Ralph completion state에 prompt-to-artifact checklist와 fresh verification evidence를 기록하고 read-back한다.

## 제출 검증

- Technical Report 본문이 최대 4페이지인지 확인한다.
- PDF, Title, Abstract가 익명이며 서로 동일한 시스템 설명을 사용하는지 확인한다.
- `review-agent.md`, 구조화 결과, hash, receipt가 freeze manifest와 일치하는지 확인한다.
- 루트 `README.md`가 프로젝트 목적, 공식 upstream, ASCII architecture, 설치·실행·검증, 제출물 경로, 측정 결과, 알려진 한계를 포함하는지 확인한다.
- 루트 `README.md`의 수치와 상태가 실제 test evidence 및 `HANDOFF.md`와 일치하고 placeholder가 없는지 확인한다.
- 익명 Technical Report에는 GitHub 계정명이나 개인 식별정보를 복사하지 않는다.

# 15. Go / No-Go 기준

## Go

- mock 10편이 제한 시간 안에 10/10 완료된다.
- 필수 리뷰 필드와 점수 범위 검사가 100% 통과한다.
- 중복 게시가 0건이며 재시작 시험을 통과한다.
- post timeout 뒤 status-first reconciliation이 동작한다.
- 실제 플랫폼 adapter와 제출 상태 판정 방식이 확인된다.
- Technical Report, Title, Abstract가 제출 가능 상태다.
- Ralph launch 표면 하나가 실제 smoke test를 통과하고, credential 질문 없이 동작한다.
- `.omx/context` snapshot과 `RALPH_GOAL.md` hash가 존재한다.
- `HANDOFF.md`와 `CHECKPOINT.json`이 존재하고 15:30 이후 자동 쓰기가 종료된다.

## Live 절대시간 게이트

- T+00:00–00:45. `LIVE_DISCOVERY`로 assigned count, claim semantics, PDF 접근, form field, 성공 표시를 실제 화면에서 확인한다.
- T+00:45–15:00. Normal mode로 Worker 3개, draft timeout 120초, targeted repair 최대 20초를 사용한다.
- T+15:00. `posted_verified < 70% assigned_count`면 fast mode로 전환하고 draft timeout을 60초로 줄인다.
- T+20:00. `posted_verified < assigned_count - 1`이면 concise-valid emergency mode로 전환한다.
- T+22:00. 새로운 고비용 분석을 중단하고 미완료 리뷰의 최소 유효 완성을 우선한다.
- T+23:30. 새로고침을 포함한 전체 status audit을 시작한다.
- T+24:30. 신규 side effect를 중단하고 ledger와 outbox를 export한다.
- Worker 3개는 16:30–16:35에 mock 1건으로 prewarm하며 build/verifier agent는 종료한다.

## No-Go와 축소 전략

- Worker 3개가 불안정하면 Worker 2개로 줄이고 개별 timeout을 단축한다.
- 브라우저 자동화가 불안정하면 병렬 독해는 유지하되 Root의 UI 작업을 완전 직렬화한다.
- verifier agent가 병목이면 라이브에서 제외하고 결정론적 validator만 사용한다.
- API 계약이 끝내 불명확하면 UI의 실제 표시 상태를 source of truth로 삼고 추정 endpoint는 사용하지 않는다.
- 자동 브라우저가 실패하면 `MANUAL_PLATFORM.md` 절차로 전환한다. Agent는 `outbox/<paper_id>.json`과 clipboard-ready text를 계속 만들고, 사람은 Safari에서 claim/download/post만 수행한다.

# 16. Human Editing과 16:30 제출 계획

- 15:30–15:40. Handoff와 실패 항목을 먼저 읽고 실제 주장 범위를 결정한다.
- 15:40–16:00. Technical Report를 사람이 편집하고 익명성, 4페이지, 표·수치, 과장 표현을 확인한다.
- 16:00–16:10. Title과 Abstract를 PDF의 최종 주장과 일치시킨다.
- 16:10–16:20. OpenAgentReview에 PDF, Title, Abstract를 업로드하고 제출한다.
- 16:20–16:25. 제출 receipt와 화면 상태를 확인하고 로컬에 기록한다.
- 16:25–16:30. 변경 공지와 16:35 실행 조건만 확인한다. 보고서 재작성은 하지 않는다.

사람 편집 시 계획 또는 mock 결과를 실제 플랫폼 성능으로 표현하지 않는다. Ralph가 검증하지 못한 주장은 삭제하거나 limitation으로 표시한다.

# 17. 최종 산출물

- 설치 가능한 Codex Skill 1개.
- live Worker용 native agent와 구축·감사용 native agent.
- `review-agent.md` 동결본과 hash manifest.
- 10편 구조화 리뷰 결과와 게시 receipt 원장.
- 익명 Technical Report PDF, Title, Abstract.
- mock, failure injection, restart 검증 기록.
- 라이브 운영 runbook과 최종 10/10 상태 감사 기록.
- `RALPH_GOAL.md`, `FAILURE_LEDGER.md`, `CHECKPOINT.json`, `HANDOFF.md`.
- GitHub 메인 페이지용 루트 `README.md`.

# 18. 현재 미확정 사항

- OpenAgentReview의 실제 로그인 방식과 세션 유지 방식.
- 논문 claim과 review post가 UI 전용인지 API가 제공되는지 여부.
- 게시 성공을 판정할 수 있는 status/receipt의 정확한 형태.
- 실제 PDF 획득 방식과 텍스트 추출 품질.
- OpenAgentReview 행사 venue가 열릴 정확한 시각과 실제 platform adapter.

이 네 항목은 구현 시작 직후 read-only 탐색 또는 실제 화면 관찰로 확인한다. 확인 전에는 코드나 문서에 가짜 endpoint와 selector를 넣지 않는다.

# 19. 주최측 추가 공식 링크의 적용

| 자료 | 계획상 용도 | Track 2 판단 |
| --- | --- | --- |
| 공식 Skills 저장소 | `auto-research`와 Track 2 템플릿의 upstream source of truth. | 반드시 사용하고 commit/hash를 고정한다. |
| VESSL 크레딧 페이지 | 승인된 참가자의 GPU 크레딧 수령. | 공식 Skill이 Track 2-only에는 GPU·VESSL이 불필요하다고 명시하므로 현재 범위에서 제외한다. |
| 오전 세션 한·영 슬라이드 | Codex Goal, 행사 운영, W&B/VESSL 설명의 보조 근거. | 접근 가능한 원문을 확보하면 제출 계약과 충돌 여부만 확인한다. |
| Luma 행사 페이지 | 일정, 트랙 정의, Ralph Loop 제한의 공개 기준. | 16:30 hard cut과 16:35–17:00 리뷰 구간을 재확인했다. |

VESSL 크레딧과 슬라이드 페이지는 Luma에 공식 링크로 게시된 사실까지 확인했다. 현재 웹 수집 경로에서는 두 페이지의 본문을 직접 가져오지 못했으므로, 내용을 추정해 계획에 넣지 않는다.

# 20. 근거 문서

- [정리된 Track 2 참가자 가이드](../../guides/20260712_Track-2-Participant-Guide.md).
- [Notion 참가자 가이드 전사본](../../references/notion-participant-guide/20260712_Ralphthon-ICML-Participant-Guide-transcript.md).
- [현재 Review Agent 템플릿](../../deliverables/ralphthon_track2_codex_package/templates/review-agent.md).
- [현실화된 패키지 계획](ralphthon-track2-feasible-package.md).
- [현재 Track 2 패키지](../../deliverables/ralphthon_track2_codex_package/README.md).
- [주최측 공식 Ralphthon ICML Skills 저장소](https://github.com/team-attention/ralphthon-icml).
- [주최측 공식 auto-research Skill](https://github.com/team-attention/ralphthon-icml/tree/main/skills/auto-research).
- [VESSL 크레딧 페이지](https://claim-vessl-credits.team-attention.com).
- [오전 세션 한·영 슬라이드](https://ralphthon-icml-presentation.team-attention.com/slides.bi.html).
- [Luma 행사 페이지](https://luma.com/hjuo7auc).
