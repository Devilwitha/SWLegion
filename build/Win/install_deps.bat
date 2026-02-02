@echo off
REM Install Python Dependencies for Star Wars Legion
REM Run this script before building

echo ============================================
echo Installing Star Wars Legion Dependencies
echo ============================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found!
    echo Please install Python 3.8+ from https://python.org
    pause
    exit /b 1
)

echo Python found: 
python --version
echo.

REM Upgrade pip
echo Upgrading pip...
python -m pip install --upgrade pip

REM Install requirements
echo.
echo Installing dependencies...
pip install -r requirements.txt

if errorlevel 1 (
    echo.
    echo ERROR: Dependency installation failed!
    pause
    exit /b 1
)

echo.
echo ============================================
echo Dependencies installed successfully!
echo ============================================
echo.
echo You can now run 'build.bat' to compile the application.
echo.
pause