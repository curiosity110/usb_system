@echo off
set PORT=8787
start "" "%~dp0Astraion.exe" --db "%~dp0data\astraion.db" --port %PORT%
timeout /t 2 /nobreak > NUL
start "" "http://localhost:%PORT%"

