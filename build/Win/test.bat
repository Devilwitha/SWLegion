@echo off
REM Quick Test Script v2.1
REM Tests if the compiled executable works correctly

echo ================================================
echo Star Wars Legion - Executable Test Script v2.1
echo ================================================
echo.

if not exist "dist\SWLegion\SWLegion.exe" (
    echo ERROR: Executable not found!
    echo Please run build.bat first.
    pause
    exit /b 1
)

echo Found executable: dist\SWLegion\SWLegion.exe
echo File size: 
dir "dist\SWLegion\SWLegion.exe" | findstr SWLegion.exe
echo.

echo Checking data files...
if not exist "dist\SWLegion\_internal\bilder\SW_legion_logo.png" (
    echo WARNING: Logo PNG missing
) else (
    echo ✓ SW Legion logo found
)

if not exist "dist\SWLegion\_internal\utilities" (
    echo WARNING: utilities directory missing
) else (
    echo ✓ utilities directory found
)

echo.
echo Testing executable launch...
echo (Program will open in new window - close it to continue)
echo.

REM Start the program and wait a moment
start "" "dist\SWLegion\SWLegion.exe"
timeout /t 3 >nul

echo.
echo Test completed!
echo.
echo If the program opened successfully, the build is working.
echo If you encountered errors, check the console output.
echo.
pause