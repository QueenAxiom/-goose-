@echo off
title Mission Control helper
cd /d "%~dp0"
start "" http://127.0.0.1:8765
python control.py
pause
