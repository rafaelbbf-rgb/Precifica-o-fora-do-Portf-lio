@echo off
chcp 65001 >nul
title Calculadora Executiva de Precificacao - Office Total
cd /d "%~dp0"

echo ============================================================
echo   Calculadora Executiva de Precificacao - Office Total
echo ============================================================
echo.

REM --- Verifica o Python -------------------------------------------------
where python >nul 2>nul
if errorlevel 1 (
    echo [ERRO] Python nao encontrado.
    echo Instale o Python 3.10 ou superior em:
    echo   https://www.python.org/downloads/
    echo Importante: marque a opcao "Add Python to PATH" durante a instalacao.
    echo.
    pause
    exit /b
)

REM --- Cria o ambiente virtual na primeira execucao ----------------------
if not exist ".venv" (
    echo Preparando o ambiente pela primeira vez. Isso pode levar 1-2 minutos...
    python -m venv .venv
    call ".venv\Scripts\activate"
    python -m pip install --upgrade pip --quiet
    pip install -r requirements.txt --quiet
) else (
    call ".venv\Scripts\activate"
)

echo.
echo Abrindo o aplicativo no navegador...
echo (Para fechar o programa, feche esta janela preta.)
echo.

REM --- Inicia o app (o Streamlit abre o navegador automaticamente) -------
streamlit run app.py

pause
