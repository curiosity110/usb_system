@echo off
setlocal ENABLEDELAYEDEXPANSION

set BASE=%~dp0
set PORT=8787
set EXE=%BASE%Astraion.exe
set DB=%BASE%data\astraion.db
set LOGDIR=%BASE%logs

if not exist "%BASE%data" mkdir "%BASE%data"
if not exist "%BASE%data\backups" mkdir "%BASE%data\backups"
if not exist "%LOGDIR%" mkdir "%LOGDIR%"

start "" "%EXE%" --db "%DB%" --port %PORT% --logdir "%LOGDIR%"
timeout /t 2 >nul
start "" http://localhost:%PORT%

endlocal
