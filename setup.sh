#!/usr/bin/env bash
# Creates an ISOLATED virtual environment and installs all dependencies.
# Usage:  bash setup.sh
set -euo pipefail

cd "$(dirname "$0")"

PYTHON="${PYTHON:-python3}"
VENV_DIR=".venv"

echo "[>] Creating virtual environment in ${VENV_DIR}"
"${PYTHON}" -m venv "${VENV_DIR}"

# shellcheck disable=SC1091
source "${VENV_DIR}/bin/activate"

echo "[>] Upgrading pip"
python -m pip install --upgrade pip

echo "[>] Installing dependencies (this may take a while)"
pip install -r requirements.txt

echo
echo "[OK] Environment ready. Next steps:"
echo "     source ${VENV_DIR}/bin/activate"
echo "     python download_models.py   # once, needs internet"
echo "     python ingest.py            # indexes ./documents"
echo "     python chat.py              # chat with your documents"
