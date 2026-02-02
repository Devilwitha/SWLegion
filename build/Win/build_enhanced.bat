@echo off
echo.
echo ====================================
echo Star Wars Legion - Complete Build
echo ====================================
echo.

:: Clean previous builds
if exist dist rmdir /s /q dist
if exist build rmdir /s /q build

echo Building executable with PyInstaller...
echo.

pyinstaller SWLegion.spec

if %ERRORLEVEL% equ 0 (
    echo.
    echo ====================================
    echo Build successful!
    echo ====================================
    echo.
    
    :: Run a quick test to check logging
    echo Testing executable with logging...
    echo.
    
    cd dist\SWLegion
    echo Running test execution...
    SWLegion.exe --test 2>&1
    
    cd ..\..
    
    if exist "dist\SWLegion\legion_app.log" (
        echo.
        echo Log file created successfully!
        echo Last 10 lines of log:
        echo ----
        type "dist\SWLegion\legion_app.log" | more +0 | tail -10
        echo ----
    ) else (
        echo Warning: No log file created during test
    )
    
    echo.
    echo Output directory: dist\SWLegion\
    echo Executable: dist\SWLegion\SWLegion.exe
    echo.
    echo You can now run the installer build with: build_installer.bat
) else (
    echo.
    echo ====================================
    echo Build failed!
    echo ====================================
    echo.
    echo Please check the output above for errors.
)

echo.
pause