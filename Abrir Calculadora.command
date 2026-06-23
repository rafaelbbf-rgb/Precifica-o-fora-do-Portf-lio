#!/bin/bash
# Lancador de um clique para macOS (clique duplo).
cd "$(dirname "$0")"
echo "Calculadora Executiva de Precificacao - Office Total"
if ! command -v python3 >/dev/null 2>&1; then
  echo "Python 3 nao encontrado. Instale em https://www.python.org/downloads/"
  read -n1 -p "Pressione qualquer tecla para sair..."
  exit 1
fi
if [ ! -d ".venv" ]; then
  echo "Preparando o ambiente pela primeira vez..."
  python3 -m venv .venv
  source .venv/bin/activate
  pip install --upgrade pip --quiet
  pip install -r requirements.txt --quiet
else
  source .venv/bin/activate
fi
echo "Abrindo o aplicativo no navegador..."
streamlit run app.py
