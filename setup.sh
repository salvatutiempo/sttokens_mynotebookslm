#!/usr/bin/env bash
# Crea un entorno virtual AISLADO e instala todas las dependencias.
# Uso:  bash setup.sh
set -euo pipefail

cd "$(dirname "$0")"

PYTHON="${PYTHON:-python3}"
VENV_DIR=".venv"

echo "[>] Creando entorno virtual en ${VENV_DIR}"
"${PYTHON}" -m venv "${VENV_DIR}"

# shellcheck disable=SC1091
source "${VENV_DIR}/bin/activate"

echo "[>] Actualizando pip"
python -m pip install --upgrade pip

echo "[>] Instalando dependencias (puede tardar)"
pip install -r requirements.txt

echo
echo "[OK] Entorno listo. Próximos pasos:"
echo "     source ${VENV_DIR}/bin/activate"
echo "     python download_models.py   # una vez, necesita internet"
echo "     python ingest.py            # indexa ./documents"
echo "     python chat.py              # chatea con tus documentos"
