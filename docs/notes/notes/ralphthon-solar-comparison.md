---
type: Project
title: 랄프톤(Solar Open2) vs 랄프톤(Codex) 비교 실험
description: 랄프톤 해커톤에서 Codex로 실행한 랄프루프를 Solar Open 2 + Claude Code로 재현하고, 정성·정량 비교 분석하는 실험 프로젝트
tags: [ralphthon, solar-open2, codex, ralph-loop, comparison, experiment]
timestamp: 2026-07-17T12:00:00Z
status: planning
---

# 랄프톤(Solar Open2) vs 랄프톤(Codex) 비교 실험

## 🎯 프로젝트 목적

랄프톤(Ralphthon @ ICML 2026)에서 Codex CLI가 `RALPH_GOAL.md`를 읽고 3시간 동안 자율적으로 P0 deliverables를 구현한 **랄프루프(Ralph Loop)**를,

**Solar Open 2를 백엔드로 하는 Claude Code**로 재현하여 두 모델의 자율 실행 능력을 정성·정량 비교하는 것이 목적이다.

핵심 비교 질문:
- Solar Open 2가 RALPH_GOAL.md의 14개 P0 항목을 얼마나 이해하는가?
- Claude(Codex) 대비 Solar의 자율적 작업 수행 능력은 어떤가?
- 랄프루프 실행 중 에러/복구/완료 패턴이 어떻게 다른가?

---

## 📁 랄프톤 원본 자료 위치

| 항목 | 경로 | 비고 |
|------|------|------|
| 랄프톤 원본 저장소 | `/tmp/ralphthon-analysis/` | Ralphthon 제출용 저장소 복제본 |
| 랄프톤 GitHub | `https://github.com/changwonjeon/20260712-ralphthon-submit` | 원본 저장소 |
| Solar 작업 공간 | `_Upstage/` | 현재 프로젝트 루트 |

⚠️ **원본 저장소(`/tmp/ralphthon-analysis/`)는 읽기 전용 참조로 유지**하고, `_Upstage`에서는 작업용 사본만 생성한다.

---

## 🧩 랄프루프(Ralph Loop) 구조 요약

### 실행 구조

```
./work/start-ralph-loop.sh START-RALPH
  ↓
./work/run-ralph-direct.sh 실행
  ↓
RALPH_GOAL.md 내용 읽기
  ↓
codex -a never -s workspace-write -C <root> "$task_text"
  ↓
$ralph \n\n <RALPH_GOAL.md> 프롬프트로 Codex 자율 실행
```

### 핵심 실행 명령

```bash
# run-ralph-direct.sh
goal_text="$(<RALPH_GOAL.md)"
task_text=$'$ralph\n\n'"$goal_text"
export OMX_RALPH_APPEND_INSTRUCTIONS_FILE="$ROOT/.omx/ralph/session-instructions.md"
exec codex -a never -s workspace-write -C "$ROOT" "$task_text"
```

### RALPH_GOAL.md 핵심 내용

- **P0 Deliverables**: 14개 항목 (Skill 설치, Worker 구현, mock 10편 3회, schema/품질/중복 검증, Technical Report PDF, Title/Abstract, review-agent.md, README, 실행 증적, HANDOFF.md 생성)
- **Absolute Time Gates**: 12:30–15:30 (3시간), 15:20 기능 동결, 15:30 자동 쓰기 종료
- **Autonomy Contract**: 사용자 질문 금지, credential/MFA 요구 금지, 원격 Git push 금지, 로컬 commit 허용
- **Validation Gates**: mock 10편 3회, schema 100%, duplicate 0건, timeout/restart/reconciliation 검증

---

## 🔄 비교 실험 설계 (3단계)

### A안: 정성 비교 (Qualitative)

| 비교 항목 | 내용 |
|-----------|------|
| P0 이해도 | RALPH_GOAL.md의 14개 P0 항목을 모델이 얼마나 정확히 파악하는가 |
| 작업 분해 능력 | 큰 목표를 작은 단계로 분해하여 실행하는 능력 |
| 에러 대응 | 실패 시 원인을 파악하고 복구하는 능력 |
| 산출물 품질 | 생성된 코드/문서의 완성도, schema 준수, 주석 품질 |

### B안: 과정 기록 (Process Recording)

| 기록 항목 | 수집 방법 | 출력 |
|-----------|-----------|------|
| 전체 세션 로그 | tmux pipe-pipe-pipe → 로그 파일 | `data/results/ralpthon/solar-session.log` |
| P0 진행 체크포인트 | 각 P0 완료 시 자동 캡처 | `data/results/ralpthon/checkpoints/checkpoint-{N}.json` |
| Git 변경 추적 | `git log --oneline --name-only` 주기 캡처 | `data/results/ralpthon/gitlog/` |
| 에러/실패 원장 | FAILURE_LEDGER.md 형식 Solar 버전 | `data/results/ralpthon/failure-ledger.md` |
| 실행 시간 측정 | 시작/종료 timestamp 기록 | `data/results/ralpthon/timing.json` |
| 생성된 파일 목록 | `find` + 파일 트리 diff | `data/results/ralpthon/files.json` |

### C안: 정량 비교 (Quantitative)

| 비교 지표 | 측정 방법 | 기준값(Codex) |
|-----------|-----------|---------------|
| P0 완료율 | 14개 P0 중 완료 수 / 전체 | Codex: 14/14 (P0 full pass) |
| 산출물 생성률 | 생성된 파일 수 / 기대 파일 수 | Codex: 29/29 files |
| 스키마 준수율 | review-draft.schema.json 검증 통과율 | Codex: 30/30 (100%) |
| 중복 방지율 | 중복 post/commit 발생 여부 | Codex: 0 duplicate |
| 시간 지표 | P0별 소요 시간, 총 실행 시간 | Codex: ~3시간 |
| 에러 복구율 | 실패 후 자동 복구 성공 비율 | Codex: 4/4 recovery |
| 리뷰 품질 | TP/FP/FN, F1 score (mock 10편) | Codex: TP 20, FP 0, FN 0, F1 1.0 |
| 안정성 | 실행 중 사용자 개입 필요 횟수 | Codex: 0 (완전 자율) |

---

## 📋 실험 진행 단계

### Phase 1: 랄프톤 자료 복사 (Copy & Setup)
- 랄프톤 원본(`/tmp/ralphthon-analysis/`)에서 핵심 파일만 선택하여 `_Upstage/docs/experiments/ralphthon/`에 복사
- 필수 복사: `RALPH_GOAL.md`, `work/*.sh`, `.codex/skills/`, `.codex/agents/`, `.omx/plans/`, `fixtures/`, `src/`, `tests/`
- 제외: `.git/`, `_private/`, `tmp/`, 실행 결과물(`outbox/`, `manifests/`, `clipboard/`)

### Phase 2: 실행 스크립트 수정 (Adapt for Solar)
- `work/run-ralph-direct.sh` → `src/scripts/ralpthon/run-ralph-solar.sh`
  - `codex` CLI → `claude` CLI (`--dangerously-skip-permissions`)
  - `task_text` 생성 로직은 유지
- `work/start-ralph-loop.sh` → `src/scripts/ralpthon/start-ralph-solar.sh`
  - tmux 세션 관리 유지 (필요시 단순화)
  - watchdog 유지 또는 단순화

### Phase 3: 비교 기록 시스템 구축 (Comparison Framework)
- 세션 로깅 스크립트: `tmux pipe-pipe-pipe` 설정 + 로그 수집
- 체크포인트 자동 캡처: P0 완료 감지 시 `CHECKPOINT.json` 스냅샷
- 정량 지표 계산기: `src/scripts/ralpthon/compare.py`
- 비교 리포트 템플릿: `docs/experiments/ralphthon/solar-vs-codex-comparison.md`

### Phase 4: 랄프루프 실행 (Solar Execution)
- 사용자가 `--dangerously-skip-permissions`로 Claude Code 재실행
- 랄프루프 시작: `./src/scripts/ralpthon/start-ralph-solar.sh START-RALPH`
- 실행 중 모니터링: `tmux attach -t ralphthon-solar` (읽기 전용)
- 실행 완료 후 산출물 수집

### Phase 5: 비교 분석 및 리포트 작성 (Analysis & Report)
- Solar 실행 결과를 Codex 결과와 정성·정량 비교
- `docs/experiments/ralphthon/solar-vs-codex-comparison.md` 작성
- 인사이트 도출 및 다음 실험 방향 제안

---

## 📂 Suggested Directory Structure (in _Upstage)

```
_Upstage/
├── docs/experiments/ralphthon/
│   ├── RALPH_GOAL.md              # 포크된 목표 파일
│   ├── plan.md                    # 실행 계획 (Plan 참조)
│   ├── context.md                 # 컨텍스트 스냅샷
│   ├── solar-vs-codex-comparison.md  # 최종 비교 리포트
│   └── handoff-template.md        # Handoff 템플릿
├── src/scripts/ralpthon/
│   ├── start-ralph-solar.sh       # 수정된 런처
│   ├── run-ralph-solar.sh         # 수정된 실행 스크립트
│   ├── compare.py                 # 비교 지표 계산 스크립트
│   └── record-session.sh          # 세션 로깅 스크립트
├── docs/notes/models/ralphthon/
│   └── agents/                    # TOML 에이전트 정의
├── docs/notes/skills/ralphthon/
│   └── track2-review-agent/       # 스킬 정의
├── data/results/ralpthon/solar/
│   ├── session.log                # 전체 세션 로그
│   ├── checkpoints/               # P0별 체크포인트
│   ├── gitlog/                    # Git 변경 로그
│   ├── failure-ledger.md          # 실패 원장
│   ├── timing.json                # 시간 지표
│   └── files.json                 # 생성/수정 파일 목록
├── data/results/ralpthon/codex/
│   └── (기존 랄프톤의 ledger.jsonl, CHECKPOINT.json 등 참조)
└── data/datasets/ralphthon-mock/
    └── paper-00*.md              # Mock 논문 10편
```

---

## 📝 실험 로그 (Execution Log)

### 2026-07-17 — Day 1: Planning & Setup

**활동**: 랄프톤 저장소 분석, 비교 실험 Plan 작성, 위키 문서화

**관찰**:
- 랄프루프의 본질은 `codex -a never -s workspace-write`로 `$ralph\n\n<RALPH_GOAL.md>`를 전달하는 것
- RALPH_GOAL.md가 100줄 이상의 상세 계획으로, 자체적으로 P0, 타임라인, 검증 기준, 자율성 규칙을 포함
- Codex와 Claude Code는 서로 다른 CLI이므로, 비교 시 "프롬프트 이해도"와 "P0 수행 능력"에 초점
- 랄프톤 원본은 `/tmp/ralphthon-analysis/`에 있으며 `_Upstage`와 완전히 분리됨

**결정**:
- 랄프톤 원본은 `/tmp/`에 그대로 유지, `_Upstage`에서는 작업용 사본만 생성
- 비교 실험은 `docs/experiments/ralphthon/` 디렉토리에서 진행
- Phase 1~5로 단계적 접근

**다음 액션**:
- 사용자가 `--dangerously-skip-permissions`로 Claude Code 재실행
- Plan 승인 후 Phase 1(랄프톤 자료 복사) 시작
- README.md에 실험 프로젝트 섹션 추가

---

## 🔗 Related

- [RALPH_GOAL.md 원문](../experiments/ralphthon/RALPH_GOAL.md) (Phase 1 완료 후 생성)
- [Plan](../plans/greedy-brewing-cookie.md)
- [LLM-Wiki: Models](../models/)
- [LLM-Wiki: Experiments](../experiments/)
- [Upstage Solar Open 2](../models/solar-open2.md)
