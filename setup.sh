#!/usr/bin/env bash

set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="${PROJECT_ROOT}/.venv"
REQUIREMENTS_FILE="${PROJECT_ROOT}/requirements.txt"

if command -v python3 >/dev/null 2>&1; then
	PYTHON_BIN="${PYTHON_BIN:-python3}"
elif command -v python >/dev/null 2>&1; then
	PYTHON_BIN="${PYTHON_BIN:-python}"
else
	echo "Error: Python 3.10 or later is required."
	exit 1
fi

"${PYTHON_BIN}" -c 'import sys; raise SystemExit(sys.version_info < (3, 10))' || {
	echo "Error: Python 3.10 or later is required."
	exit 1
}

if [[ ! -d "${VENV_DIR}" ]]; then
	echo "Creating virtual environment in .venv..."
	"${PYTHON_BIN}" -m venv "${VENV_DIR}"
fi

echo "Installing project dependencies..."
"${VENV_DIR}/bin/python" -m pip install --upgrade pip
"${VENV_DIR}/bin/python" -m pip install -r "${REQUIREMENTS_FILE}"

echo "Starting URL Shortener API at http://localhost:8000"
echo "API documentation: http://localhost:8000/docs"
exec "${VENV_DIR}/bin/python" -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload