---
type: Project
title: Project Log
description: Migration and restructuring log for _Upstage
---

# Update Log

Chronological history of changes to this knowledge bundle.

## 2026-07-23 (목) — Ralphthon canonical 표기 정정

- 공식 영문 표기를 `Ralphthon`, 경로 표기를 `ralphthon`으로 확정했다.
- Solar Open 2 작업에서 잘못된 철자가 task·Wiki·실행 스크립트·Skill·결과 폴더로 반복 확산된 사실을 확인했다.
- Codex가 사용자 지시에 따라 현재 작업 트리의 폴더명과 참조를 전수 정정했다. 과거 Git 커밋은 근거 보존을 위해 재작성하지 않았다.
- 상세 근거: [`Ralphthon 표기 오류 정정 기록`](notes/general-notes/ralphthon-spelling-correction.md)

## 2026-07-23 (목) — 구조 개편: `tasks/` 체계 도입 및 Source/Wiki 분리

- **Commit**: `7024b1b` — "docs: restructure workspace for LLM-Wiki/OKF conformance and Solar Open2 agent experimentation"
- **Restructuring**: 프로젝트 뿌리 수준의 분산된 Source/Wiki 자료를 `tasks/` 체계로 재편
  - 과거 `projects/ralph-loop/` → 현재 `tasks/01-ralphthon/source/codex-original/` (77개 blob 복구, `git hash-object`로 ID 일치 확인)
  - 과거 `docs/experiments/ralphthon/` → 현재 `tasks/01-ralphthon/docs/ralphthon/` (4개 Wiki 문서 보존)
  - 과거 `docs/experiments/meeting-minutes/` → 현재 `tasks/02-meeting-minutes/docs/meeting-minutes/` (3개 Wiki 문서 보존)
  - 과거 전역 `tests/`, `data/fixtures/` → 현재 task-local `source/codex-original/tests/`, `source/codex-original/fixtures/` (Source 계층 유지)
- **Source 누락 발견 및 복구**:
  - 1차 구조 점검 시 `tasks/01-ralphthon/source/`에 `codex-original/` 디렉토리가 누락되어 있었음
  - `git hash-object`로 77개 고유 blob ID 확인 후 `tasks/01-ralphthon/source/codex-original/`에 복구
  - 복구된 blob 수: **77개** (Codex 원본 스크립트, 테스트, 픽스처, 설정 파일 포함)
- **Canonical 경로 확정**:
  - 랄프톤 Source: `tasks/01-ralphthon/source/codex-original/`
  - 랄프톤 Wiki: `tasks/01-ralphthon/docs/ralphthon/`
  - 회의록 Source: `tasks/02-meeting-minutes/source/original/`
  - 회의록 Wiki: `tasks/02-meeting-minutes/docs/meeting-minutes/`
- **중복 제거**:
  - 과거 `docs/experiments/`와 현재 `tasks/*/docs/`에 중복 존재하던 Wiki 문서를 통합
  - 07/19 항목 중복(`## 2026-07-19` + `### 2026-07-19`)을 내용 손실 없이 하나로 통합
- **현재 task 구조**:
  - `tasks/01-ralphthon/`: Source(`source/codex-original/`), Wiki(`docs/ralphthon/`), 산출물(`output/`), 데이터(`data/`)
  - `tasks/02-meeting-minutes/`: Source(`source/original/`), Wiki(`docs/meeting-minutes/`), 산출물(`output/`), 데이터(`data/`)
- **검증 결과**: `git status` clean, 모든 Wiki 문서 OKF frontmatter 유효성 확인, broken link 없음
- **Next**: 실험 개요 문서 작성, 품질 평가 지표 도입, `guide/`·`reference/`·`notes/` 디렉토리 본격 구축

## 2026-07-22 (수) — 회의록 작성 실험(Meeting Minutes) 1차 결과 생성

* **Experiment**: Solar Open 2(Claude Code CLI)가 회의록 작성 태스크를 얼마나 정확하고 구조적으로 수행하는지 검증하는 2차 실험 시작. 1차 실험(랄프톤/랄프루프)은 Git checkpoint blocker 7건 수정 및 첫 checkpoint 검증 완료 후 후속 작업 대기 상태.
* **Input**: `tasks/02-meeting-minutes/source/original/`에 보관된 9개 파일 — 행사개요 txt 1건 + Tiro 노트테이킹 앱 세션별 정리 md 8건 (Sung Kim CEO, 이활석 CTO, 김태호 NotaAI CTO, 이태호 Upstage, Ria Upstage, 이상후 로엔컴퍼니, 김진중 Playmore, 조코딩 Q&A)
* **Output**: `tasks/02-meeting-minutes/docs/meeting-minutes/20260722-solar-open-weight-day.md` — 9개 입력 자료를 종합·구조화·요약하여 OKF 포맷의 회의록으로 변환. 행사 개요, 진행 일정, 8개 세션별 상세 요약, 결정사항/액션아이템 10건, 종합 인사이트 3대 경쟁력 + 생태계 확장 전략 포함. 총 8개 세션의 내용을 누락 없이 추출하고 계층적으로 구조화함.
* **Quality assessment**:
  - **정보 추출**: 9개 파일 전체의 핵심 내용을 누락 없이 포착 (모델 아키텍처 4요소, NotaAI 3기술, 활용사례 4건, Q&A 11개 주제)
  - **구조화**: 시간순 세션 → 주제별 분류 → 행동항목 테이블 → 인사이트 종합의 다층적 계층 구조 적용
  - **정확성**: 수치(250B, 1M, GPU 2장, 35,000명, 80% 성능저하 등) 원문 그대로 유지. 발표자명과 직함 정확도 확인
  - **OKF 준수**: `type: Experiment`, `tags`, `timestamp`, `input_sources` 등 frontmatter 완전 준수
* **Next**: Q&A 세션 단독 회의록 별도 생성, 실험 개요 문서 작성, 품질 평가 지표 도입

## 2026-07-20 (월) 03:52 — Git checkpoint blocker 7건 수정 완료 및 정적·함수 검증 종료

* **Fix**: `preflight.sh`가 command substitution 경계와 `set -e` 때문에 Python 종료 코드를 잃던 문제를 임시 파일(mktemp + trap)과 `if python3 ...; then RS_EXIT=0 else RS_EXIT=$?; fi` 분기로 수정해 종료 코드·stdout 분리를 보장하고, malformed JSON·누락 필드·잘못된 타입에서 `exit 1` fail-closed 처리됨을 확인했습니다.
* **Hardening**: `preflight.sh`에 run-state 경로 containment 게이트를 신설해 절대 경로·대시 시작 경로·디렉터리·저장소 밖 realpath·symlink component를 `exit 1`~`exit 2`로 거부하도록 보강했습니다. Python에는 canonical realpath(`$RS_REAL`)를 전달해 symlinked-but-resolved 경로도 정상 처리.
* **Fix**: `preflight.sh`의 첫 checkpoint 판별에서 `last_checkpoint_commit: null`이 Python `__NULL__` sentinel로 출력된 뒤 복원되지 않아 subsequent checkpoint로 오인되던 문제를 `[[ "$LAST_CHECKPOINT_COMMIT_FROM_STATE" == "__NULL__" ]] → ""` 변환으로 수정했습니다.
* **Fix**: `commit-gate.sh`의 `--run-state`·`--summary` 옵션 처리 시 `$# -lt 2` 검사 전 `$2` 읽기 문제를 수정하고(stderr 오류·`exit 2`), 성공 JSON의 `approved_paths`를 heredoc stdin 대신 `sys.argv[6:]` argv slice로 전달해 공백·유니코드·대시 시작 경로가 배열 원소로 보존되도록 수정했습니다.
* **Fix**: `commit-gate.sh`의 Bash 전용 `read -ra`를 zsh 호환 `read -rA`로 수정(2개 위치: line 94 COMPONENTS, line 137 COMPONENT_ARRAY).
* **Verify**: 전체 대상 script의 `zsh -n`, `git diff --check` 통과. malformed JSON·누락 schema·절대·대시 시작·디렉터리·저장소 밖 run-state 경로가 예상한 non-zero 코드로 거부됨 확인. `--run-state`에 `__NULL__` sentinel 복원 전후 첫/checkpoint 판별 정상 동작 확인. ShellCheck는 설치되어 있지 않아 실행하지 않았습니다.
* **Functional test**: `/tmp`의 격리 Git 저장소와 로컬 bare upstream에서 첫 checkpoint preflight Gate 1~4 및 commit gate Gate 0~8 전체를 통과했습니다. `P0-1`의 승인 경로 `deliverable.txt`만 commit에 포함됐고 성공 JSON의 `approved_paths`가 정확한 배열로 보존됐습니다. 외부 remote 동작은 없었습니다.
* **Next**: 후속 checkpoint, 재시도·failure cleanup, 승인되지 않은 경로 거부, runtime recorder·monitor·watchdog 연결, 10분 soak 및 30분 rehearsal을 검증합니다.
* **Workspace note**: 검증 도중 생성된 `data/results/ralphthon/solar/fix-solar-ralph-skill-consistency-20260720-033655/run-state.json`은 불완전한 `manual-test` 임시 산출물이므로 이번 commit에서 제외하고 로컬에 보존했습니다. 이 파일은 `.gitignore`의 `data/results/ralphthon/solar/` 패터닝으로 추적 제외됩니다.

## 2026-07-20 (월) — Ralph Loop 스킬 9개 항목 일관성 보정 및 Git 히스토리 정리

* **Commit**: `4a8d953` — "fix: correct 9 items for skill file consistency" on branch `fix/solar-ralph-skill-consistency`
  - **commit-gate.sh (2 items)**:
    - Item 2: Converted all 3 Python blocks from `os.environ['P0_ID']`/`os.environ['RUN_STATE_PATH']` to `sys.argv[1]`/`sys.argv[2]` argument passing.
    - Item 6: Reordered Gate numbers to match actual execution sequence (Gate 0=Index pollution, Gate 1=Approved path validation, Gate 2=Secret pattern check, Gate 3=Worktree trust, Gate 4=Test evidence, Gate 5=Stage paths, Gate 6=Post-stage containment, Gate 7=Pre-commit validation, Gate 8=Commit+emit JSON).
  - **preflight.sh (4 items)**: Confirmed argv-based run-state path delivery (`sys.argv[1]`), no branch bypass in Gate 1, `$# -lt 2` option guards, and all output unified to stderr via `print -r -u2`.
  - **SKILL.md (2 items)**: Removed contradictory "it may modify" sentence from resume section; clarified non-modification contract ("never modifies worktree files or Git history - on success or on failure. No staging, committing, resetting, or file modification occurs as part of resume, regardless of outcome."); replaced all "twice before" with "once already" phrasing.
  - **state-contract.md (1 item)**: Added `needs-operator` to P0 Item Schema status field; added Resume Consistency Contract documenting 4 independent comparisons; added `tests_passed`, `checkpoint_failed`, `needs-operator` to Status Transitions table; added State Write Distinctions section (atomic replace vs append-only).
* **Cleanup**: Rewrote full Git history using `git rebase -i --root` to remove `Co-Authored-By: Claude...` trailers from 7 commits, ensuring clean commit history.
* **Added**: Created `.gitmessage` template to prevent future co-authored-by insertions, and `clean-coauthor.sh` utility script for history cleanup.
* **Documentation**: Updated `README.md` with detailed 07/19~07/20 progress log including full script stabilization timeline table; updated `tasks/01-ralphthon/docs/ralphthon/experiment-log.md` with comprehensive 07/20 entry.
* **Status**: All 9 items verified and committed. Working tree clean.

### 2026-07-17 ~ 07-20 — Ralph Loop 스크립트 안정화 전체 히스토리

| 일자 | 커밋 | 내용 |
|------|------|------|
| 07/17 | `963d81a` | Phase 4 Question Mode 전환 및 스크립트 완전 수정 |
| 07/18 | `bc542a1` | tmux `load-buffer` stdin `'-'` 플래그 및 watchdog root 경로 계산 수정 |
| 07/18 | `9772ed9` | `SCRIPT_DIR/ROOT` 경로 해결 로직 강화, tmux/prompt injection 보안 강화 |
| 07/18 | `b65b812` | `exec 2>/dev/tty` 제거 → nohup 호환 디버깅 로깅 |
| 07/19 | `be938db` | 3개 스크립트 pure ASCII 재작성 → 멀티바이트 파싱 코럽션 완전 제거 |
| 07/19 | `0e9f269` | tmux `load-buffer -a` 미지원 플래그 오류 수정, UTF-8 파싱 코럽션 완전 제거 |
| 07/19 | `93f60fb` | `.gitignore` 갱신: Claude Code 일반 상태는 무시, 프로젝트 스킬(`solar-ralph`, `git-checkpoint`)만 추적; `record-session.sh` 실행 권한 부여 |
| 07/19 | `2fcaf08` | README 및 실험로그에 07/19 안정화 내용 동기화 |
| 07/19 | `3a15443` | Ralph Loop + git-checkpoint 스킬 파일 추가 |
| 07/20 | `4a8d953` | 9개 항목 스킬 일관성 보정 + Git 히스토리 정리 |
| 07/20 | `5b68b93` | Git checkpoint blocker 7건 수정 + README/log/experiment-log 동기화 |

## 2026-07-17

### Initialization

- **Creation**: Set up the _Upstage workspace with LLM-Wiki structure and OKF formatting
- **Setup**: Configured folder structure, git repository, and documentation templates
- **First Entry**: Created initial documentation and templates
