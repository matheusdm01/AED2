#!/usr/bin/env bash
# Reprodução em um comando: cria o ambiente virtual, instala as dependências fixadas e roda tudo.
set -euo pipefail
cd "$(dirname "$0")"
[ -d .venv ] || python3 -m venv .venv
# shellcheck disable=SC1091
. .venv/bin/activate
pip install -q -r requirements.txt
python reproduzir.py
