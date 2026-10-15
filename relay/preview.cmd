@echo off
rem Local preview of every site draft. Open http://127.0.0.1:8800/sites/<domain>/ (nothing is published).
cd /d %~dp0
python -m http.server 8800 --bind 127.0.0.1
