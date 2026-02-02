@echo off
echo.
echo ====================================
echo Star Wars Legion - Portable Package
echo ====================================
echo.

:: Check if the executable exists
if not exist "dist\SWLegion\SWLegion.exe" (
    echo ERROR: SWLegion.exe not found in dist\SWLegion\
    echo Please run build.bat first to create the executable.
    echo.
    pause
    exit /b 1
)

:: Create output directory
if not exist "Portable" mkdir Portable

:: Copy the entire SWLegion directory
echo Copying application files...
xcopy "dist\SWLegion" "Portable\SWLegion\" /E /I /Y /Q

:: Create a launcher script in the root
echo Creating launcher...
echo @echo off > "Portable\Start_SWLegion.bat"
echo cd /d "%%~dp0SWLegion" >> "Portable\Start_SWLegion.bat"
echo SWLegion.exe >> "Portable\Start_SWLegion.bat"

:: Create README file
echo Creating README...
echo Star Wars Legion - Portable Version > "Portable\README.txt"
echo. >> "Portable\README.txt"
echo Installation Instructions: >> "Portable\README.txt"
echo 1. Extract this folder to any location on your computer >> "Portable\README.txt"
echo 2. Double-click "Start_SWLegion.bat" to run the application >> "Portable\README.txt"
echo. >> "Portable\README.txt"
echo No installation required! >> "Portable\README.txt"
echo. >> "Portable\README.txt"
echo System Requirements: >> "Portable\README.txt"
echo - Windows 10 or later >> "Portable\README.txt"
echo - No additional software required >> "Portable\README.txt"

:: Create a ZIP file if 7zip is available
where 7z >nul 2>nul
if %ERRORLEVEL% equ 0 (
    echo Creating ZIP archive...
    cd Portable
    7z a -tzip "..\SWLegion_Portable.zip" *
    cd ..
    echo.
    echo ====================================
    echo Portable package created successfully!
    echo ====================================
    echo.
    echo Files created:
    echo - Portable\ directory with all files
    echo - SWLegion_Portable.zip archive
    echo.
) else (
    echo.
    echo ====================================
    echo Portable package created successfully!
    echo ====================================
    echo.
    echo Files created in: Portable\ directory
    echo.
    echo Note: 7zip not found. ZIP archive not created.
    echo You can manually create a ZIP file from the Portable folder.
)

echo To distribute: Share the Portable folder or SWLegion_Portable.zip
echo Users can extract and run Start_SWLegion.bat
echo.
pause