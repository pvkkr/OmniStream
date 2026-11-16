@echo off
title OmniStream - Video Downloader & VLC Player
cd /d "%~dp0"
echo Starting OmniStream Desktop App...
python app.py
if errorlevel 1 (
    echo.
    echo An error occurred while running the application.
    pause
)
