@echo off
rem Yanımda'yı başlatır: gerekirse Docker'ı kurar, servisleri açar ve siteyi tarayıcıda gösterir.
chcp 65001 >nul
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0scripts\start-windows.ps1" %*
if errorlevel 1 (
  echo.
  echo Başlatma tamamlanamadı. Yukarıdaki hata mesajına bakın.
)
pause
