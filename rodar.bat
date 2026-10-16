@echo off
REM Abre o Painel ESTAT no navegador. Funciona com dois cliques, de qualquer lugar.
cd /d "%~dp0"
python -m streamlit run app.py
if errorlevel 1 (
  echo.
  echo Se apareceu "No module named streamlit", rode antes:  python -m pip install -r requirements.txt
  pause
)
