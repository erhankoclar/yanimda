@echo off
rem Yanımda servislerini durdurur. Veriler silinmez.
chcp 65001 >nul
cd /d "%~dp0"
docker compose down
pause
