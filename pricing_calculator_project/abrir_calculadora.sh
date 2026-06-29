#!/bin/bash
# Lancador para Linux:  ./abrir_calculadora.sh
cd "$(dirname "$0")"
command -v python3 >/dev/null 2>&1 || { echo "Instale o Python 3.10+"; exit 1; }
[ -d .venv ] || { python3 -m venv .venv; source .venv/bin/activate; pip install -U pip -q; pip install -r requirements.txt -q; }
source .venv/bin/activate
streamlit run app.py
