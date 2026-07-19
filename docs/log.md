# Update Log

Chronological history of changes to this knowledge bundle.

## 2026-07-20 (월) 03:51 — Git checkpoint blocker 수정 및 첫 성공 경로 검증

* **Fix**: `preflight.sh`가 command substitution 경계와 `set -e` 때문에 Python 실패 코드를 잃던 문제를 임시 파일과 명시적 `if` 종료 코드 포착으로 수정했습니다.
* **Hardening**: run-state 경로를 저장소 상대 경로로 제한하고 절대 경로, 대시 시작 경로, 디렉터리, 저장소 밖 resolve와 symlink component를 거부하도록 보강했습니다.
* **Fix**: `last_checkpoint_commit: null`의 `__NULL__` sentinel을 빈 값으로 복원해 첫 checkpoint가 후속 checkpoint로 오인되던 문제를 수정했습니다.
* **Fix**: `commit-gate.sh`의 `--run-state`·`--summary` 인자 가드, 성공 JSON의 `approved_paths` argv 전달, Bash 전용 `read -ra`를 zsh용 `read -rA`로 수정했습니다.
* **Verify**: 전체 대상 script의 `zsh -n`, `git diff --check`, malformed JSON·누락 schema fail-closed와 경로 거부 테스트를 통과했습니다. ShellCheck는 설치되어 있지 않아 실행하지 않았습니다.
* **Functional test**: `/tmp`의 격리 Git 저장소와 로컬 bare upstream에서 첫 checkpoint preflight 및 commit gate 전체를 통과했습니다. `P0-1`의 승인 경로 `deliverable.txt`만 commit `d0b0e84`에 포함됐고 성공 JSON의 `approved_paths`가 정확했습니다. 외부 원격 동작은 없었습니다.
* **Next**: 후속 checkpoint, 공백·유니코드 경로, 실패 후 index cleanup, 승인되지 않은 경로 거부, runtime recorder·monitor·watchdog 연결, 10분 soak 및 30분 rehearsal을 검증합니다.
* **Workspace note**: 검증 도중 생성된 `data/results/ralpthon/solar/fix-solar-ralph-skill-consistency-20260720-033655/run-state.json`은 불완전한 `manual-test` 임시 산출물이므로 이번 commit에서 제외하고 로컬에 보존했습니다.

## 2026-07-19 (일) — Ralph Loop 스크립트 안정화 커밋 및 푸시

* **Update**: Committed and pushed (`git push origin main`) the following changes to the `solar-open2-experiments` repository:
  - **`.gitignore` update**: Refined to exclude Claude Code's general state (`/.claude/*`) while explicitly tracking project skills (`solar-ralph/`, `git-checkpoint/`) for reproducibility.
  - **`src/scripts/ralpthon/record-session.sh`**: Added executable permission (`chmod +x`).
* **Update**: Updated `README.md` — refreshed the "Solar Open 2 Comparison Experiment Project" section with current status (Phase 5 진행 중) and a summary of the recent script stabilization improvements (UTF-8 corruption fix, tmux robustness, nohup compatibility, path hardening, security hardening).
* **Update**: Updated `docs/log.md` — added today's entry documenting the git push and the Ralph Loop script stabilization work.
* **Update**: Updated `docs/experiments/experiment-log.md` — added today's entry with details of the script stabilization and workflow improvements.
* **Commit Log**: `59c7689` — "chore: exclude Claude Code general state but track project skills in .gitignore; make record-session.sh executable"
  - Builds on previous commit `3c2387d` (fix: tmux load-buffer flag error, UTF-8 corruption elimination), `628876e` (refactor: pure ASCII rewrite), `748b9c4` (fix: nohup-compatible debug logging), `ed24e63` (fix: SCRIPT_DIR/ROOT resolution, tmux/prompt injection hardening), and `918dc92` (fix: tmux load-buffer stdin flag, watchdog path calculation).

### 2026-07-17

* **Initialization**: Established the LLM-Wiki + OKF knowledge bundle structure with LLM-Wiki categories (People, Models, Papers, Projects, Notes, Writing) and OKF-formatted documents (YAML frontmatter + Markdown body). Set up folder hierarchy under `docs/` with guide, reference, experiments, notes, and templates.
* **Creation**: Added 5 document templates (Model, Paper, Experiment, Person, Project) following OKF conventions.
* **Creation**: Created initial guides: Getting Started, Hermes Agent integration, Claude Code with Solar Open2, and OKF Document Authoring.
* **Creation**: Documented Solar Open2 model specifications and capabilities under `docs/reference/`.
* **Creation**: Set up experiment tracking with log and index files.
* **Update**: Configured git repository with `.gitignore` excluding `_private/` directory for sensitive credentials and personal notes.

### 2026-07-19 (일) — Ralph Loop 스크립트 안정화 커밋 및 푸시

* **Update**: Committed and pushed (`git push origin main`) the following changes to the `solar-open2-experiments` repository:
  - **`.gitignore` update**: Refined to exclude Claude Code's general state (`/.claude/*`) while explicitly tracking project skills (`solar-ralph/`, `git-checkpoint/`) for reproducibility.
  - **`src/scripts/ralpthon/record-session.sh`**: Added executable permission (`chmod +x`).
* **Update**: Updated `README.md` — refreshed the "Solar Open 2 Comparison Experiment Project" section with current status (Phase 5 진행 중) and a summary of the recent script stabilization improvements (UTF-8 corruption fix, tmux robustness, nohup compatibility, path hardening, security hardening).
* **Update**: Updated `docs/log.md` — added today's entry documenting the git push and the Ralph Loop script stabilization work.
* **Update**: Updated `docs/experiments/experiment-log.md` — added today's entry with details of the script stabilization and workflow improvements.
* **Commit Log**: `59c7689` — "chore: exclude Claude Code general state but track project skills in .gitignore; make record-session.sh executable"
  - Builds on previous commit `3c2387d` (fix: tmux load-buffer flag error, UTF-8 corruption elimination), `628876e` (refactor: pure ASCII rewrite), `748b9c4` (fix: nohup-compatible debug logging), `ed24e63` (fix: SCRIPT_DIR/ROOT resolution, tmux/prompt injection hardening), and `918dc92` (fix: tmux load-buffer stdin flag, watchdog path calculation).

### 2026-07-20 (월) — Ralph Loop 스킬 9개 항목 일관성 보정 및 Git 히스토리 정리

* **Commit**: `4a8d953` — "fix: correct 9 items for skill file consistency" on branch `fix/solar-ralph-skill-consistency`
  - **commit-gate.sh (2 items)**:
    - Item 2: Converted all 3 Python blocks from `os.environ['P0_ID']`/`os.environ['RUN_STATE_PATH']` to `sys.argv[1]`/`sys.argv[2]` argument passing.
    - Item 6: Reordered Gate numbers to match actual execution sequence (Gate 0=Index pollution, Gate 1=Approved path validation, Gate 2=Secret pattern check, Gate 3=Worktree trust, Gate 4=Test evidence, Gate 5=Stage paths, Gate 6=Post-stage containment, Gate 7=Pre-commit validation, Gate 8=Commit+emit JSON).
  - **preflight.sh (4 items)**: Confirmed argv-based run-state path delivery (`sys.argv[1]`), no branch bypass in Gate 1, `$# -lt 2` option guards, and all output unified to stderr via `print -r -u2`.
  - **SKILL.md (2 items)**: Removed contradictory "it may modify" sentence from resume section; clarified non-modification contract ("never modifies worktree files or Git history - on success or on failure. No staging, committing, resetting, or file modification occurs as part of resume, regardless of outcome."); replaced all "twice before" with "once already" phrasing.
  - **state-contract.md (1 item)**: Added `needs-operator` to P0 Item Schema status field; added Resume Consistency Contract documenting 4 independent comparisons; added `tests_passed`, `checkpoint_failed`, `needs-operator` to Status Transitions table; added State Write Distinctions section (atomic replace vs append-only).
* **Cleanup**: Rewrote full Git history using `git rebase -i --root` to remove `Co-Authored-By: Claude...` trailers from 7 commits, ensuring clean commit history.
* **Added**: Created `.gitmessage` template to prevent future co-authored-by insertions, and `clean-coauthor.sh` utility script for history cleanup.
* **Documentation**: Updated `README.md` with detailed 07/19~07/20 progress log including full script stabilization timeline table; updated `docs/experiments/experiment-log.md` with comprehensive 07/20 entry.
* **Status**: All 9 items verified and committed. Working tree clean.
