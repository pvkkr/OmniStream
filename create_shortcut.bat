@echo off
title Create OmniStream Desktop Shortcut
cd /d "%~dp0"
echo Creating Desktop Shortcut...
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0create_desktop_shortcut.ps1"
echo.
pause
