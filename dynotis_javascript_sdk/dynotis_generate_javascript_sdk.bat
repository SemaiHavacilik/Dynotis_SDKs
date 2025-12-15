@echo off
echo ========================================================
echo      DYNOTIS JAVASCRIPT SDK GENERATOR
echo ========================================================

:: 1. Navigate to the script's directory
cd /d "%~dp0"

:: 2. Run the Node.js build script
call node build_sdk.js

echo.
pause
