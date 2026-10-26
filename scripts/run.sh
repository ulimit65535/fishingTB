#!/usr/bin/env bash
set -euo pipefail

PROJECT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
cd -- "$PROJECT_DIR"

if [[ ! -d .venv ]]; then
    if ! command -v python3 >/dev/null 2>&1; then
        echo "请先安装 Python 3.11 或更新版本。" >&2
        exit 1
    fi
    python3 -c 'import sys; sys.exit(0 if sys.version_info >= (3, 11) else "需要 Python 3.11 或更新版本。")'
    echo "正在创建虚拟环境 .venv …"
    python3 -m venv .venv
fi

if [[ ! -x .venv/bin/python || ! -f .venv/bin/activate ]]; then
    echo ".venv 不可用，请修复或移走该目录后重试。" >&2
    exit 1
fi

source .venv/bin/activate

# Install once; leave the marker absent on failure so the next run retries.
if [[ ! -f .venv/.fishingtb-ready ]]; then
    python -m pip install -r requirements.txt
    touch .venv/.fishingtb-ready
fi

exec python "$PROJECT_DIR/main.py" "$@"
