@echo off
REM Star Wars Legion Game Companion & AI Simulator
REM Windows Build Script using PyInstaller v2.1
REM
REM New Features:
REM - Fixed module imports for PyInstaller executable
REM - SW Legion icon included
REM - Direct module execution instead of subprocess
REM - All utilities modules embedded
REM
REM Prerequisites:
REM - Python 3.8+ installed
REM - pip install pyinstaller pillow requests

echo ============================================
echo Star Wars Legion - Windows Build Script v2.1
echo ============================================
echo.
echo Features:
echo - SW Legion icon ✓
echo - Fixed module imports ✓ 
echo - Direct module execution ✓
echo - Marker system with emojis ✓
echo.

REM Check if PyInstaller is installed
python -c "import PyInstaller" 2>nul
if errorlevel 1 (
    echo ERROR: PyInstaller not found
    echo Please install with: pip install pyinstaller
    pause
    exit /b 1
)

REM Check if Pillow is installed
python -c "import PIL" 2>nul
if errorlevel 1 (
    echo ERROR: Pillow PIL not found
    echo Please install with: pip install Pillow
    pause
    exit /b 1
)

echo Dependencies check passed.
echo.
echo Starting build process...
echo.

REM Clean previous build
if exist dist rmdir /s /q dist
if exist build rmdir /s /q build
if exist __pycache__ rmdir /s /q __pycache__

REM Build with PyInstaller using spec file
python -m PyInstaller --clean --noconfirm SWLegion.spec

if errorlevel 1 (
    echo.
    echo ERROR: Build failed
    pause
    exit /b 1
)

echo.
echo ============================================
echo Build completed successfully
echo ============================================
echo.
echo Executable location: dist\SWLegion\SWLegion.exe
echo.
echo You can now distribute the entire dist\SWLegion folder
echo.

REM Copy additional files
if exist "..\..\sw_legion_logo.png" copy "..\..\sw_legion_logo.png" "dist\SWLegion\"
if exist "..\..\README.md" copy "..\..\README.md" "dist\SWLegion\"

echo Additional files copied.
echo.
echo Build finished! Press any key to exit...
pause >nul