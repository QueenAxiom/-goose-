@echo off
REM Axiom start-of-day: make sure Mission Control is up, open it in Chrome, open the ECC window.
REM Colibri, n8n, Ollama, Sofia and Wispr Flow start on their own from the Startup folder.
set "REPO=C:\Users\DELL\axiom-enterprises"
set "MC_URL=http://127.0.0.1:8765/"

powershell -NoProfile -Command "if (-not (Get-NetTCPConnection -LocalPort 8765 -State Listen -ErrorAction SilentlyContinue)) { Start-Process pythonw.exe -ArgumentList 'control.py' -WorkingDirectory '%REPO%\mission-control' -WindowStyle Hidden }"

REM wait up to 60s for Mission Control to answer
powershell -NoProfile -Command "for ($i=0; $i -lt 30; $i++) { if (Get-NetTCPConnection -LocalPort 8765 -State Listen -ErrorAction SilentlyContinue) { exit 0 }; Start-Sleep -Seconds 2 }; exit 1"

start "" chrome "%MC_URL%"
start "ECC" cmd /k "cd /d %REPO% && claude"
