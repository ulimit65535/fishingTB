#!/bin/zsh
set -eu
PROJECT_DIR="$(cd -- "$(dirname -- "$0")" && pwd)"
cd -- "$PROJECT_DIR"
exec "$PROJECT_DIR/start.sh" "$@"
