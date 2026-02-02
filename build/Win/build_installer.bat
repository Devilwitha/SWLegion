@echo off
echo.
echo ====================================
echo Star Wars Legion - Installer Build
echo ====================================
echo.

:: Check if Inno Setup is installed
where iscc >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo ERROR: Inno Setup Compiler (iscc.exe) not found in PATH!
    echo Please install Inno Setup from: https://jrsoftware.org/isinfo.php
    echo Or add Inno Setup directory to your PATH environment variable.
    echo.
    pause
    exit /b 1
)

:: Check if the executable exists
if not exist "dist\SWLegion\SWLegion.exe" (
    echo ERROR: SWLegion.exe not found in dist\SWLegion\
    echo Please run build.bat first to create the executable.
    echo.
    pause
    exit /b 1
)

:: Create installer output directory if it doesn't exist
if not exist "InstallerSetup" mkdir InstallerSetup

echo Building installer...
echo.

:: Compile the installer
iscc SWLegion_Setup.iss

if %ERRORLEVEL% equ 0 (
    echo.
    echo ====================================
    echo Installer built successfully!
    echo ====================================
    echo.
    echo Output: InstallerSetup\SWLegion_Installer.exe
    echo.
    
    :: Check if installer was created
    if exist "InstallerSetup\SWLegion_Installer.exe" (
        echo Installer size: 
        dir "InstallerSetup\SWLegion_Installer.exe" | findstr SWLegion_Installer.exe
        echo.
        echo You can now distribute the installer to users.
    )
) else (
    echo.
    echo ====================================
    echo ERROR: Installer build failed!
    echo ====================================
    echo.
    echo Please check the output above for error details.
)

echo.
pause