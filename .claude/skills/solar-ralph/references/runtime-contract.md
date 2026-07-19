# Runtime Contract

> Environment and infrastructure contract for `/solar-ralph` execution. Not a skill — read-only reference for the skill and for humans auditing the run.

## tmux Session Lifecycle

The Ralph Loop run is hosted inside two `tmux` sessions created by the launcher (`src/scripts/ralpthon/start-ralph-solar.sh`):

| Session | Purpose | Command |
|---------|---------|---------|
| `ralphthon-loop` | Hosts the interactive `claude-upstage` REPL that executes `/solar-ralph` | `tmux new-session -d -s ralphthon-loop -c <repo-root> <run-script>` |
| `ralphthon-deadline` | Hosts the deadline watchdog that monitors elapsed time and inactivity | `tmux new-session -d -s ralphthon-deadline <watchdog-script>` |

### Session Isolation

- The `ralphthon-loop` session runs `claude-upstage` with **no CLI flags** (the `claude-upstage` wrapper does not pass `--add-dir` or other flags through; project skills in `.claude/skills/` are discovered automatically when the session starts in the repo root).
- The initial prompt injected into the session is the concatenation of the `$ralph` prefix string and the contents of the task spec file at the path provided to `start`. This is done via `tmux load-buffer` + `tmux paste-buffer` before the first user interaction.
- The `ralphthon-deadline` session runs independently and monitors elapsed time from the launcher's `start_time` timestamp.

### Session Termination

- The deadline watchdog terminates the `ralphthon-loop` session by sending `Ctrl+C` (twice, with 1-second delay) followed by `tmux kill-session -t ralphthon-loop`.
- The watchdog then kills its own session: `tmux kill-session -t ralphthon-deadline`.
- `/solar-ralph finalize` is expected to be invoked before the watchdog's hard termination, either by the user or by the deadline proximity check in `step` mode (when fewer than 600 seconds remain). If `finalize` is not invoked before hard termination, the handoff is considered incomplete and the run status is treated as `terminated-unfinalized` by whatever post-run analysis is performed.

## Deadline Enforcement

- The deadline is specified in seconds as the second argument to `/solar-ralph start`.
- The launcher records `start_time=$(date +%s)` at launch time. The deadline is `start_time + <deadline-seconds>`.
- The watchdog checks elapsed time every 60 seconds (`CHECK_INTERVAL=60`). When elapsed ≥ deadline, it triggers hard termination.
- `/solar-ralph step` performs a **soft deadline check**: if fewer than 600 seconds remain, it skips implementation and proceeds directly to `finalize deadline`. This provides a grace period before the hard termination.
- The deadline is **not** adjustable after `start` is called. If the user needs more time, the run must be finalized and a new run started.

## Inactivity Detection

- The watchdog monitors activity by capturing the `ralphthon-loop` pane content every `CHECK_INTERVAL` seconds.
- Activity is detected when the pane content changes (as measured by string length comparison in the current implementation; future revisions should use content hash).
- If no activity is detected for `INACTIVITY_THRESHOLD` seconds (default 180), the watchdog sends a continuation prompt to the session. This prompt reminds the model of elapsed time, remaining time, and requests a status update. It does **not** inject new instructions or modify the task.
- `/solar-ralph step` must **not** send continuation prompts while the model is actively working. Continuation prompts are the watchdog's responsibility, not the skill's.

## Launcher Interface

The launcher (`src/scripts/ralpthon/start-ralph-solar.sh`) performs the following in order:

1. Verifies the confirmation token (`START-RALPH`) is provided.
2. Checks that `RALPH_GOAL.md` (or the specified task spec) exists.
3. Checks that the working tree has no uncommitted tracked changes (`git status --porcelain --untracked-files=no`).
4. Kills any existing `ralphthon-loop` or `ralphthon-deadline` sessions.
5. Creates the `ralphthon-loop` session running `run-ralph-solar.sh` (which execs `claude-upstage`).
6. Creates the `ralphthon-deadline` session running `ralph-deadline-watchdog.sh`.
7. Waits 10 seconds for `claude-upstage` to initialize.
8. Loads the concatenated `$ralph` + task spec into a tmux buffer and pastes it into the `ralphthon-loop` session.
9. Sends Enter to submit the prompt.
10. Checks for permission prompts and auto-responds with `y` if detected (Question Mode).

The launcher does **not** start the recorder (`record-session.sh`) or the checkpoint monitor (`capture-checkpoints.sh`). These are independent utilities that must be started separately if used.

## claude-upstage Wrapper Constraints

- `claude-upstage` accepts: `--model <id>`, `-c`/`--continue`, `-r`/`--resume [id]`, `models`, `doctor`, `login`, `logout`, `install`.
- `claude-upstage` does **not** pass arbitrary CLI flags to the underlying `claude` process. It parses its own limited flag set and rejects unknown flags.
- Project skills in `.claude/skills/<name>/SKILL.md` are discovered automatically when Claude Code is started in a directory containing a `.claude/` folder with that structure. No `--add-dir` flag is needed for skills within the current workspace.
- The `claude-upstage` wrapper does not inhibit skill discovery. Skills are found by Claude Code's internal discovery mechanism, not by CLI flags.
- The `allowed-tools` frontmatter in a skill's `SKILL.md` defines which Bash commands the model may invoke during that skill's execution. This is separate from the `permissions` configuration in `.claude/settings.json` and `.claude/settings.local.json`.

## Recorder and Checkpoint Monitor

- `record-session.sh` captures tmux pane output to log files using `tmux pipe-pane`. It is **not** started by the launcher. If used, it must be started manually before the run begins.
- `capture-checkpoints.sh` polls `session.log` for size changes and attempts to detect P0 completion via keyword heuristics. It is **not** started by the launcher. If used, it must be started manually.
- The current implementation of `capture-checkpoints.sh` uses `ROOT="${SCRIPT_DIR:h}"`, which resolves to `src/scripts/` rather than the repository root. This is a known limitation. The `/solar-ralph` skill and its state files use the correct repository root as determined by the launcher. Checkpoint artifacts should be written relative to `data/results/ralpthon/solar/<run-id>/` as determined by the launcher's ROOT calculation.

## Process Isolation

- Each run uses a unique `run-id` (`solar-ralph-<YYYYMMDD-HHMMSS>`). All state files, logs, and artifacts are namespaced under `data/results/ralpthon/solar/<run-id>/`.
- tmux session names (`ralphthon-loop`, `ralphthon-deadline`) are reused across runs. The launcher kills existing sessions before creating new ones.
- The watchdog and the main loop session are independent processes. Killing one does not automatically kill the other, though the launcher's termination sequence attempts to kill both.
- Broad process kill commands (e.g., `pkill -9 -f claude-upstage`) are **forbidden**. Only the tmux session names and the specific launchers they spawned should be terminated.

## Permissions and Auto-Acceptance

- The launcher includes a Question Mode heuristic: if the pane content matches patterns like `permission|allow|Permanent|Confirm|do you want|abort|denied|yes/no|y/N|y/n`, it sends `y` + Enter.
- The `claude-upstage` wrapper does not provide a `--allow-dangerously-skip-permissions` flag. Permission prompts must be handled via tmux interaction or by pre-configuring permissions in `.claude/settings.local.json`.
- The `/solar-ralph` skill itself does not handle permission prompts. It assumes the environment (launcher + settings) has been configured to minimize interactive permission prompts for the allowed tool set.
- `allowed-tools` in the skill's frontmatter is a **pre-approval list**, not a sandbox. Commands not listed in `allowed-tools` may still be attempted by the model, but the Claude Code runtime will typically reject them. `allowed-tools` does not actively block unknown commands — it simply does not grant them a blanket pass. The actual enforcement depends on the Claude Code runtime version and configuration.
- The `permissions.allow` and `permissions.deny` in `.claude/settings.local.json` are separate from `allowed-tools` and apply globally across all skills and direct interactions. Skill-level `allowed-tools` provides a narrower, skill-specific scope on top of the global settings.

## Heartbeat and State Monitoring

- The watchdog is the primary heartbeat monitor. It does not participate in the `/solar-ralph` state machine.
- `/solar-ralph` maintains its own state in `run-state.json` and `events.jsonl`. These are updated by the skill itself, not by the watchdog or launcher.
- If the watchdog terminates the session before `/solar-ralph finalize` is invoked, the state files written up to that point are preserved in `data/results/ralpthon/solar/<run-id>/`. The handoff is incomplete but the partial state is recoverable.
