#!/bin/zsh
set -euo pipefail

SCRIPT_DIR="${0:A:h}"
ROOT="${SCRIPT_DIR:h}"
SESSION_DIR="$ROOT/data/results/ralpthon/solar"

# Default: 1 hour of logging
LOG_DURATION="${LOG_DURATION:-3600}"
TIMESTAMP="$(date +%Y%m%d_%H%M%S)"

usage() {
  cat <<EOF
Usage: $(basename "$0") [COMMAND] [OPTIONS]

Commands:
  start               Start logging tmux sessions to data/results/ralpthon/solar/
  stop                Stop logging and finalize logs
  status              Check if logging is active
  dump [SESSION]      Dump current log for a session (default: ralphthon-loop)

Options:
  --duration SECONDS  Set logging duration (default: 3600)
  --output DIR        Set output directory (default: data/results/ralpthon/solar/)

Environment:
  SESSION_DIR         Output directory (default: \$ROOT/data/results/ralpthon/solar)
  LOG_DURATION        Logging duration in seconds (default: 3600)

Examples:
  $(basename "$0") start                          # Start logging both sessions
  $(basename "$0") start --duration 7200          # Log for 2 hours
  $(basename "$0") stop                           # Stop all logging
  $(basename "$0") dump ralphthon-loop            # Dump loop session log
  $(basename "$0") dump                           # Dump default session log
EOF
  exit 0
}

# Parse arguments
COMMAND="${1:-}"
shift 2>/dev/null || true

# Parse --duration and --output
while [[ $# -gt 0 ]]; do
  case "$1" in
    --duration) LOG_DURATION="$2"; shift 2 ;;
    --output) SESSION_DIR="$2"; shift 2 ;;
    *) shift ;;
  esac
done

# Determine session names to log
SESSION_NAMES=("ralphthon-loop" "ralphthon-deadline")

# Output directory setup
mkdir -p "$SESSION_DIR"

# Function to start logging a session
start_log_session() {
  local session="$1"
  local log_file="$SESSION_DIR/${session}.log"

  # Check if session exists
  if ! tmux has-session -t "$session" 2>/dev/null; then
    echo "Warning: tmux session '$session' does not exist, skipping."
    return 0
  fi

  # Create pipe log file
  echo "=== Session logging started: $session at $(date) ===" > "$log_file"
  echo "Log file: $log_file" >> "$log_file"

  # Start pipe-pipe-pipe logging (pipe output to tee/log file)
  # tmux pipe-pipe-pipe sends all pane output to the specified command
  # Using 'cat >> file' pattern for reliable logging
  tmux pipe-pane -t "$session" -f 'cat >> '"$log_file" 2>/dev/null || true

  # Also capture the pane content at start
  tmux capture-pane -t "$session" -p >> "$log_file" 2>/dev/null || true

  echo "Started logging: $session -> $log_file"
}

# Function to stop logging a session
stop_log_session() {
  local session="$1"
  local log_file="$SESSION_DIR/${session}.log"

  if ! tmux has-session -t "$session" 2>/dev/null; then
    echo "Warning: tmux session '$session' does not exist."
    return 0
  fi

  # Stop pipe-pipe-pipe
  tmux pipe-pane -t "$session" -f 'true' 2>/dev/null || true

  # Append final capture
  echo "" >> "$log_file"
  echo "=== Session logging stopped: $session at $(date) ===" >> "$log_file"
  tmux capture-pane -t "$session" -p >> "$log_file" 2>/dev/null || true

  echo "Stopped logging: $session -> $log_file"
}

# Commands
case "$COMMAND" in
  start)
    echo "Starting session logging..."
    echo "Output directory: $SESSION_DIR"
    echo "Duration: ${LOG_DURATION}s"
    echo ""

    for session in "${SESSION_NAMES[@]}"; do
      start_log_session "$session"
    done

    echo ""
    echo "Logging started. Use '$(basename "$0") stop' to stop."
    echo "Use '$(basename "$0") status' to check status."
    echo ""

    # If duration specified, auto-stop after duration
    if [[ -n "$LOG_DURATION" && "$LOG_DURATION" =~ ^[0-9]+$ && "$LOG_DURATION" -gt 0 ]]; then
      echo "Auto-stopping in ${LOG_DURATION}s..."
      sleep "$LOG_DURATION"
      "$0" stop
    fi
    ;;

  stop)
    echo "Stopping session logging..."
    for session in "${SESSION_NAMES[@]}"; do
      stop_log_session "$session"
    done
    echo "All logging stopped."
    ;;

  status)
    echo "Checking logging status..."
    for session in "${SESSION_NAMES[@]}"; do
      if tmux has-session -t "$session" 2>/dev/null; then
        local log_file="$SESSION_DIR/${session}.log"
        if [[ -f "$log_file" ]]; then
          local size=$(wc -c < "$log_file")
          local lines=$(wc -l < "$log_file")
          echo "  $session: Active (log: $log_file, $size bytes, $lines lines)"
        else
          echo "  $session: Active (no log file yet)"
        fi
      else
        echo "  $session: Not running"
      fi
    done
    ;;

  dump)
    local target_session="${1:-ralphthon-loop}"
    local log_file="$SESSION_DIR/${target_session}.log"

    if [[ -f "$log_file" ]]; then
      echo "=== Log for $target_session ==="
      echo "Log file: $log_file"
      echo "Size: $(wc -c < "$log_file") bytes"
      echo "Lines: $(wc -l < "$log_file")"
      echo ""
      cat "$log_file"
    else
      echo "Log file not found: $log_file"
      echo "Use '$(basename "$0") start' to begin logging."
      exit 1
    fi
    ;;

  -h|--help|help)
    usage
    ;;

  *)
    echo "Unknown command: $COMMAND"
    usage
    ;;
esac
