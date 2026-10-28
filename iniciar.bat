@echo off
cd /d "%~dp0"

start "Contador de Visitantes" /min .venv\Scripts\python.exe app.py

rem Espera o servidor responder antes de abrir o telao
:esperar
timeout /t 2 /nobreak >nul
curl.exe -s -o nul http://127.0.0.1:5000/api/contagem
if errorlevel 1 goto esperar

start "" msedge --kiosk http://127.0.0.1:5000 --edge-kiosk-type=fullscreen --no-first-run
