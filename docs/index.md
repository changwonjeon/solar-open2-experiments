# Docs Directory

Knowledge bundle for Upstage Solar Open2 research and experimentation.

## Subdirectories

* [guide](guide/index.md) - Usage guides and tutorials for working with Solar Open2
* [reference](reference/index.md) - Model specifications, API references, and documentation
* [experiments](experiments/index.md) - Experiment logs, results, and findings
* [notes](notes/index.md) - Wiki-style notes organized by People, Models, Papers, Projects, Writing, and General Notes
* [templates](templates/index.md) - Document templates for creating new OKF documents

### Fresh Project Structure

After the 2026-07-22 restructuring:

- **`notes/general-notes/`** — previously `notes/notes/`, renamed to avoid double-nesting
- **`projects/ralph-loop/`** — Source layer for Codex original materials (scripts, configs, tests, fixtures)
- **`src/scripts/ralpthon/original/`** — Codex original shell scripts (start-ralph-loop.sh, run-ralph-direct.sh, ralph-deadline-watchdog.sh)
- **`_inbox/`** — Delivery folder for incoming files awaiting processing
- **`docs/AGENTS.md` + `docs/CLAUDE.md`** — Wiki-specific agent rules (CLAUDE.md = `@AGENTS.md`)

## Quick Start

1. [Getting Started Guide](../docs/guide/getting-started.md) - Set up your environment
2. [Model Reference](../docs/reference/solar-open2.md) - Learn about Solar Open2
3. [Create Notes](notes/index.md) - Start documenting your findings
