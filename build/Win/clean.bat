@echo off
REM Clean Build Artifacts
REM Removes temporary build files and output directories

echo ============================================
echo Cleaning Star Wars Legion Build Artifacts
echo ============================================
echo.

REM Remove PyInstaller build directories
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist

REM Remove Python cache directories
for /d /r . %%d in (__pycache__) do @if exist "%%d" rmdir /s /q "%%d"

REM Remove spec file temporary artifacts  
if exist SWLegion.spec.orig del SWLegion.spec.orig

echo Build artifacts cleaned.
echo.
echo Directories removed:
echo - build/
echo - dist/ 
echo - __pycache__/
echo.
echo Ready for fresh build!
pause