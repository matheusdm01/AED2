#!/usr/bin/env bash
set -e
python3 src/01_extrair.py pdfs
python3 src/02_limpar_e_construir.py
python3 src/03_primeira_analise.py
