---
type: Experiment
title: 랄프톤 Solar Open2 vs Codex 비교 실험 리포트
description: 랄프톤 해커톤에서 Codex로 실행한 랄프루프를 Solar Open2 + Claude Code로 재현하고, 정성·정량 비교 분석한 실험 리포트
tags: [ralphthon, solar-open2, codex, ralph-loop, comparison, experiment]
timestamp: 2026-07-17T12:00:00Z
status: template
---

# 랄프톤 Solar Open2 vs Codex 비교 실험 리포트

> **실험 개요**: 랄프톤(Ralphthon @ ICML 2026)에서 Codex CLI가 `RALPH_GOAL.md`를 읽고 3시간 동안 자율적으로 P0 deliverables를 구현한 **랄프루프(Ralph Loop)**를, **Solar Open 2를 백엔드로 하는 Claude Code**로 재현하여 두 모델의 자율 실행 능력을 정성·정량 비교하는 실험이다.

---

## 📊 실험 설정

| 항목 | Codex (원본) | Solar Open2 (재현) |
|------|-------------|-------------------|
| **백엔드 모델** | Codex CLI | Solar Open2 (Claude Code) |
| **실행 명령** | `codex -a never -s workspace-write -C $ROOT "$task_text"` | `claude-upstage --allow-dangerously-skip-permissions -p "$task_text"` |
| **프롬프트** | `$ralph\n\n<RALPH_GOAL.md>` | `$ralph\n\n<RALPH_GOAL.md>` |
| **실행 시간** | 12:30–15:30 (3시간) | Phase 4에서 측정 |
| **P0 항목 수** | 14개 | 14개 |
| **Mock 논문 수** | 10편 (3회 반복) | 10편 (3회 반복) |
| **비교 일자** | 2026-07-12 | 2026-07-17 (Phase 4 실행일) |

---

## 🔢 정량 비교 (Quantitative Comparison)

### 1. P0 완료율 (P0 Completion Rate)

| 지표 | Codex | Solar Open2 | 차이 | 평가 |
|------|-------|-------------|------|------|
| P0 완료 수 | 14/14 | ___/14 | | |
| P0 완료율 | 100% | ___% | | |

**Solar Open2 P0 상세 (Phase 4 실행 후 채우기)**:

| # | P0 항목 | Solar 상태 | Codex 상태 | 비고 |
|---|---------|-----------|-----------|------|
| 1 | `.codex/skills/auto-research/` upstream subtree 설치 및 hash 검증 | | ✅ 완료 | |
| 2 | `.codex/skills/ralphthon-track2-review-agent/` wrapper Skill 생성 | | ✅ 완료 | |
| 3 | `.codex/agents/` Review Worker와 build verifier/auditor 생성 | | ✅ 완료 | |
| 4 | canonical schema 보존 (Contribution, Significance, Originality, Comment) | | ✅ 완료 | |
| 5 | 각 논문 input/evidence hash per-paper manifest 동결 | | ✅ 완료 | |
| 6 | Root만 claim/post/status/ledger 소유, Worker 3개는 ReviewDraft만 반환 | | ✅ 완료 | |
| 7 | mock adapter, bounded queue, lease, atomic ledger, idempotency 구현 | | ✅ 완료 | |
| 8 | gold fixture 동결, naive single-pass baseline, TP/FP/FN 기록 | | ✅ 완료 | |
| 9 | `submission/technical-report.tex`와 `submission/technical-report.pdf` 생성 | | ✅ 완료 | |
| 10 | `submission/TITLE.txt`, `submission/ABSTRACT.txt`, `review-agent.md`, `README.md`, `HANDOFF.md` 생성 | | ✅ 완료 | |
| 11 | `outbox/<paper_id>.json`과 clipboard-ready text fallback 생성 | | ✅ 완료 | |
| 12 | mock 10편 3회 실행, assigned count 전체 완료, schema 100%, duplicate 0건 | | ✅ 완료 | |
| 13 | malformed JSON, Worker timeout, claim timeout, post timeout, process restart 주입 테스트 | | ✅ 완료 | |
| 14 | Tectonic PDF 빌드, pdfinfo 페이지 확인, 익명성·placeholder 검사 | | ✅ 완료 | |

---

### 2. 산출물 생성률 (Output Generation Rate)

| 지표 | Codex | Solar Open2 | 차이 | 평가 |
|------|-------|-------------|------|------|
| 생성된 파일 수 | 29/29 | ___/29 | | |
| 산출물 생성률 | 100% | ___% | | |

---

### 3. 스키마 준수율 (Schema Compliance Rate)

| 지표 | Codex | Solar Open2 | 차이 | 평가 |
|------|-------|-------------|------|------|
| 스키마 통과 수 | 30/30 | ___/30 | | |
| 스키마 준수율 | 100% | ___% | | |

---

### 4. 중복 방지율 (Duplicate Prevention Rate)

| 지표 | Codex | Solar Open2 | 차이 | 평가 |
|------|-------|-------------|------|------|
| 중복 발생 건수 | 0 | ___ | | |

---

### 5. 시간 지표 (Time Metrics)

| 지표 | Codex | Solar Open2 | 차이 | 평가 |
|------|-------|-------------|------|------|
| 총 실행 시간 | ~3시간 | ___시간 | | |
| 처음 P0 완료 시간 | T+__분 | T+__분 | | |
| 마지막 P0 완료 시간 | T+__분 | T+__분 | | |
| 타임아웃/재시작 횟수 | ___회 | ___회 | | |

**실행 로그**:
- Solar 실행 시작 시각: `____`
- Solar 실행 종료 시각: `____`
- P0별 소요 시간:
  - P0-1 (Skill 설치): `____`
  - P0-2~3 (Skill/에이전트 생성): `____`
  - P0-4~6 (Schema/Root/Worker): `____`
  - P0-7~8 (Mock adapter/fixture): `____`
  - P0-9~11 (제출물 생성): `____`
  - P0-12~14 (검증): `____`

---

### 6. 에러 복구율 (Error Recovery Rate)

| 지표 | Codex | Solar Open2 | 차이 | 평가 |
|------|-------|-------------|------|------|
| 실패 발생 횟수 | 4 | ___ | | |
| 복구 성공 횟수 | 4/4 | ___/___ | | |
| 복구율 | 100% | ___% | | |

**실패/복구 상세**:

| # | 실패 유형 | Codex 복구 | Solar 복구 | 비고 |
|---|-----------|-----------|-----------|------|
| 1 | Malformed JSON 주입 | ✅ 복구 | | |
| 2 | Worker timeout 주입 | ✅ 복구 | | |
| 3 | Claim timeout 주입 | ✅ 복구 | | |
| 4 | Post timeout/process restart 주입 | ✅ 복구 | | |

---

### 7. 리뷰 품질 (Review Quality)

| 지표 | Codex | Solar Open2 | 차이 | 평가 |
|------|-------|-------------|------|------|
| TP (True Positive) | 20 | ___ | | |
| FP (False Positive) | 0 | ___ | | |
| FN (False Negative) | 0 | ___ | | |
| F1 Score | 1.0 | ___ | | |

**Mock 논문 10편 리뷰 결과 상세**:

| 논문 ID | Codex 리뷰 정확도 | Solar 리뷰 정확도 | 차이 | 비고 |
|---------|------------------|------------------|------|------|
| paper-001 | | | | |
| paper-002 | | | | |
| paper-003 | | | | |
| paper-004 | | | | |
| paper-005 | | | | |
| paper-006 | | | | |
| paper-007 | | | | |
| paper-008 | | | | |
| paper-009 | | | | |
| paper-010 | | | | |

---

### 8. 안정성 (Stability)

| 지표 | Codex | Solar Open2 | 차이 | 평가 |
|------|-------|-------------|------|------|
| 사용자 개입 횟수 | 0 | ___ | | |
| 안정성 점수 | 1.0 | ___ | | |

---

## 🔍 정성 비교 (Qualitative Comparison)

### 1. RALPH_GOAL.md 이해도 (P0 Comprehension)

| 항목 | Codex | Solar Open2 | 평가 |
|------|-------|-------------|------|
| 14개 P0 항목의 의미 이해 | | | |
| 타임라인/타임게이트 인식 | | | |
| 자율성 규칙(Autonomy Contract) 준수 | | | |
| 검증 기준(Validation Gates) 파악 | | | |
| Handoff 요구사항 이해 | | | |

### 2. 작업 분해 능력 (Task Decomposition)

| 항목 | Codex | Solar Open2 | 평가 |
|------|-------|-------------|------|
| 큰 목표를 작은 단계로 분해 | | | |
| P0별 하위 태스크 식별 | | | |
| 의존성 순서 파악 | | | |
| 병렬 처리 전략 (Worker 3개) | | | |

### 3. 에러 대응 (Error Handling)

| 항목 | Codex | Solar Open2 | 평가 |
|------|-------|-------------|------|
| 에러 원인 파악 능력 | | | |
| 복구 전략 수립 | | | |
| 실패 시 축소 경로 전환 | | | |
| Failure Ledger 기록 품질 | | | |

### 4. 산출물 품질 (Output Quality)

| 항목 | Codex | Solar Open2 | 평가 |
|------|-------|-------------|------|
| 코드 완성도 | | | |
| 문서 완성도 | | | |
| Schema 준수 여부 | | | |
| 주석 품질 | | | |
| README 가독성 | | | |

---

## 📁 생성된 파일 비교 (File Generation Comparison)

### Codex 생성 파일 (29개)

| # | 파일 경로 | Codex | Solar | 비고 |
|---|-----------|-------|-------|------|
| 1 | `.codex/skills/auto-research/SKILL.md` | ✅ | | |
| 2 | `.codex/skills/auto-research/agents/openai.yaml` | ✅ | | |
| 3 | `.codex/skills/auto-research/assets/AUTORESEARCH.md` | ✅ | | |
| 4 | `.codex/skills/auto-research/assets/experiment-ledger.md` | ✅ | | |
| 5 | `.codex/skills/auto-research/assets/track-1-submission-template.md` | ✅ | | |
| 6 | `.codex/skills/auto-research/assets/track-2-agent-template.md` | ✅ | | |
| 7 | `.codex/skills/auto-research/assets/track-2-review-template.md` | ✅ | | |
| 8 | `.codex/skills/auto-research/assets/vessl-a100-run-card.md` | ✅ | | |
| 9 | `.codex/skills/auto-research/references/vessl-autoresearch-runbook.md` | ✅ | | |
| 10 | `.codex/skills/auto-research/references/workflow.md` | ✅ | | |
| 11 | `.codex/skills/auto-research/scripts/record_experiment.py` | ✅ | | |
| 12 | `.codex/skills/ralphthon-track2-review-agent/SKILL.md` | ✅ | | |
| 13 | `.codex/skills/ralphthon-track2-review-agent/agents/openai.yaml` | ✅ | | |
| 14 | `.codex/skills/ralphthon-track2-review-agent/assets/review-agent-template.md` | ✅ | | |
| 15 | `.codex/skills/ralphthon-track2-review-agent/assets/review-draft.schema.json` | ✅ | | |
| 16 | `.codex/skills/ralphthon-track2-review-agent/assets/review-output-template.json` | ✅ | | |
| 17 | `.codex/skills/ralphthon-track2-review-agent/assets/review-worker-prompt.md` | ✅ | | |
| 18 | `.codex/skills/ralphthon-track2-review-agent/assets/verifier-result.schema.json` | ✅ | | |
| 19 | `.codex/skills/ralphthon-track2-review-agent/references/review-contract.md` | ✅ | | |
| 20 | `.codex/skills/ralphthon-track2-review-agent/references/runtime-runbook.md` | ✅ | | |
| 21 | `.codex/skills/ralphthon-track2-review-agent/references/submission-contract.md` | ✅ | | |
| 22 | `.codex/skills/ralphthon-track2-review-agent/scripts/_bootstrap.py` | ✅ | | |
| 23 | `.codex/skills/ralphthon-track2-review-agent/scripts/audit_receipts.py` | ✅ | | |
| 24 | `.codex/skills/ralphthon-track2-review-agent/scripts/hash_inputs.py` | ✅ | | |
| 25 | `.codex/skills/ralphthon-track2-review-agent/scripts/run_batch.py` | ✅ | | |
| 26 | `.codex/skills/ralphthon-track2-review-agent/scripts/validate_review.py` | ✅ | | |
| 27 | `.codex/agents/track2-review-verifier.toml` | ✅ | | |
| 28 | `.codex/agents/track2-review-worker.toml` | ✅ | | |
| 29 | `.codex/agents/track2-submission-auditor.toml` | ✅ | | |
| 30 | `submission/technical-report.tex` | ✅ | | |
| 31 | `submission/technical-report.pdf` | ✅ | | |
| 32 | `submission/TITLE.txt` | ✅ | | |
| 33 | `submission/ABSTRACT.txt` | ✅ | | |
| 34 | `review-agent.md` | ✅ | | |
| 35 | `README.md` | ✅ | | |
| 36 | `MANUAL_PLATFORM.md` | ✅ | | |
| 37 | `HANDOFF.md` | ✅ | | |
| 38 | `outbox/*.json` | ✅ | | |
| 39 | `fixtures/gold.json` | ✅ | | |
| 40 | `fixtures/naive-single-pass.json` | ✅ | | |

### Solar Open2 생성 파일 (Phase 4 실행 후 채우기)

동일한 구조로 Solar가 생성한 파일을 나열한다.

| # | 파일 경로 | Solar | 비고 |
|---|-----------|-------|------|
| | | | |

---

## 📋 체크리스트 요약 (Checkpoint Summary)

**실행 환경**:
- 실행 시각: `____`
- 실행 환경: `claude-upstage --allow-dangerously-skip-permissions`
- tmux 세션: `ralphthon-loop`, `ralphthon-deadline`
- 로그 파일: `data/results/ralpthon/solar/session.log`

**체크포인트 상태**:

| # | P0 항목 | 체크포인트 파일 | 상태 | 타임스탬프 |
|---|---------|----------------|------|----------|
| 1 | Skill 설치 및 hash 검증 | `checkpoint-1.json` | | |
| 2 | Review Agent Skill 생성 | `checkpoint-2.json` | | |
| 3 | Review Worker/Verifier/Auditor 생성 | `checkpoint-3.json` | | |
| 4 | Canonical schema 보존 | `checkpoint-4.json` | | |
| 5 | Evidence hash manifest 동결 | `checkpoint-5.json` | | |
| 6 | Root/Worker 소유권 분리 | `checkpoint-6.json` | | |
| 7 | Mock adapter/queue/ledger 구현 | `checkpoint-7.json` | | |
| 8 | Gold fixture/baseline 기록 | `checkpoint-8.json` | | |
| 9 | Technical Report 생성 | `checkpoint-9.json` | | |
| 10 | Title/Abstract/README/HANDOFF 생성 | `checkpoint-10.json` | | |
| 11 | Outbox/clipboard fallback 생성 | `checkpoint-11.json` | | |
| 12 | Mock 10편 3회/검증 | `checkpoint-12.json` | | |
| 13 | Failure injection 테스트 | `checkpoint-13.json` | | |
| 14 | PDF 빌드/익명성 검사 | `checkpoint-14.json` | | |

---

## 🎯 핵심 발견사항 (Key Findings)

### Solar Open2 강점

1. 
2. 
3. 

### Solar Open2 약점

1. 
2. 
3. 

### Codex 대비 차이점

1. 
2. 
3. 

---

## 🔮 인사이트 및 다음 실험 방향 (Insights & Next Steps)

### 주요 인사이트

1. **프롬프트 이해도**: Solar Open2가 RALPH_GOAL.md의 14개 P0 항목을 얼마나 정확하게 이해하는가?
2. **자율성**: 사용자 개입 없이 3시간 동안 자율적으로 작업을 수행할 수 있는가?
3. **복구 능력**: 실패 발생 시 자동으로 복구할 수 있는가?
4. **산출물 품질**: 생성된 코드/문서의 품질은 Codex와 비교하여 어떤가?

### 다음 실험 제안

1. **다른 프롬프트 전략 테스트**: `$ralph` 대신 더 구체적인 지시문 사용
2. **다른 모델 비교**: Solar Open2 외에 다른 LLM으로 동일 실험 재현
3. **체크포인트 간격 조정**: P0 완료 감지 빈도 최적화
4. **실시간 모니터링 강화**: tmux 세션 실시간 분석 도구 개발

---

## 📎 부록 (Appendix)

### A. 실행 명령어

```bash
# Solar Open2 랄프루프 시작
./src/scripts/ralpthon/start-ralph-solar.sh START-RALPH

# tmux 세션 모니터링 (읽기 전용)
tmux attach -t ralphthon-loop
tmux attach -t ralphthon-deadline

# 세션 로그 확인
./src/scripts/ralpthon/record-session.sh dump

# 체크포인트 상태 확인
./src/scripts/ralpthon/capture-checkpoints.sh status

# 정량 비교 분석
python3 src/scripts/ralpthon/compare.py
```

### B. 데이터 파일 위치

| 데이터 유형 | 경로 |
|-------------|------|
| 세션 로그 | `data/results/ralpthon/solar/session.log` |
| 체크포인트 | `data/results/ralpthon/solar/checkpoints/checkpoint-{N}.json` |
| Git 로그 | `data/results/ralpthon/solar/gitlog/` |
| 실패 원장 | `data/results/ralpthon/solar/failure-ledger.md` |
| 시간 지표 | `data/results/ralpthon/solar/timing.json` |
| 파일 목록 | `data/results/ralpthon/solar/files.json` |
| 비교 결과 | `data/results/ralpthon/solar/comparison-summary.json` |

### C. 관련 문서

- [RALPH_GOAL.md](./RALPH_GOAL.md)
- [랄프톤 비교 실험 위키](./solar-vs-codex-comparison.md)
- [Phase 2: 실행 스크립트](../../../../src/scripts/ralpthon/run-ralph-solar.sh)
- [Phase 2: 시작 스크립트](../../../../src/scripts/ralpthon/start-ralph-solar.sh)
- [Phase 3: 세션 로깅](../../../../src/scripts/ralpthon/record-session.sh)
- [Phase 3: 체크포인트 캡처](../../../../src/scripts/ralpthon/capture-checkpoints.sh)
- [Phase 3: 비교 분석기](../../../../src/scripts/ralpthon/compare.py)

---

*이 리포트는 Phase 4(Solar 실행) 완료 후 실제 데이터로 채워집니다. 현재는 템플릿 상태입니다.*
