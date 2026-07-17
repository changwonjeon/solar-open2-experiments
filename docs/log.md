# Update Log

Chronological history of changes to this knowledge bundle.

## 2026-07-17

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
