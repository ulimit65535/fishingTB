#!/usr/bin/env bash
set -euo pipefail

PROJECT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
cd -- "$PROJECT_DIR"

if [[ "$(uname -s)" == Darwin ]]; then
    exec /usr/bin/osascript "$PROJECT_DIR/scripts/start_iterm.applescript" \
        "$PROJECT_DIR/scripts/run.sh" "$@"
fi

exec /bin/bash "$PROJECT_DIR/scripts/run.sh" "$@"
