# Update Log

Chronological history of changes to this knowledge bundle.

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

### 2026-07-17 (오후) — Ralph Loop 비교 실험 Planning

* **Creation**: Created `docs/notes/notes/ralphthon-solar-comparison.md` — comprehensive wiki documenting the Ralph Loop comparison experiment plan (Solar Open 2 vs Codex). Includes experiment design (A/B/C comparison), directory structure, and execution phases.
* **Update**: Updated `README.md` — simplified for public consumption (removed internal guides: setup, workflow, security, contribution guidelines). Added "Solar Open 2 Comparison Experiment Project" section describing the Ralph Loop reproduction experiment.
* **Update**: Updated `CLAUDE.md` git author to `changwonjeon <changwon.jeon@gmail.com>` via `git filter-branch` and force-push.
* **Update**: Updated `README.md` with experiment project section linking to the comparison wiki.
* **Creation**: Created `docs/experiments/` directory for experiment records.
* **Creation**: Updated `docs/log.md` with today's changes and experiment tracking log.
* **Planning**: Created comparison experiment plan at `.claude/plans/greedy-brewing-cookie.md` covering 5 phases: (1) Copy Ralphthon materials, (2) Adapt scripts for Solar/Claude, (3) Build comparison recording framework, (4) Execute Ralph Loop with Solar, (5) Analyze and write comparison report.
