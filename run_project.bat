@echo off
setlocal
cd /d "%~dp0"
if not exist "venv\Scripts\python.exe" (
    echo Creating virtual environment...
    python -m venv venv
    if errorlevel 1 (
        echo ERROR: Python is not installed or not in PATH.
        pause
        exit /b 1
    )
)
echo Installing/updating dependencies...
venv\Scripts\python.exe -m pip install --upgrade pip
venv\Scripts\python.exe -m pip install -r requirements.txt
if errorlevel 1 (
    echo ERROR: Dependency installation failed.
    pause
    exit /b 1
)
echo Starting Lost & Found Intelligence Center...
venv\Scripts\python.exe main.py
if errorlevel 1 pause
endlocal
