@echo off
REM Search journal files for pyRevit test output

echo Searching journal files for REVBOT_TEST_SUCCESS...
echo.

REM Get today's date for journal file naming
for /f "tokens=2-4 delims=/ " %%a in ('date /t') do (set mydate=%%c%%a%%b)

REM Search in common journal file locations
set JOURNAL_DIR=%USERPROFILE%\AppData\Local\Autodesk\Revit\Autodesk Revit 2018\Journals
if not exist "%JOURNAL_DIR%" set JOURNAL_DIR=%USERPROFILE%\AppData\Local\Autodesk\Revit\Autodesk Revit 2019\Journals
if not exist "%JOURNAL_DIR%" set JOURNAL_DIR=%USERPROFILE%\AppData\Local\Autodesk\Revit\Autodesk Revit 2020\Journals
if not exist "%JOURNAL_DIR%" set JOURNAL_DIR=%USERPROFILE%\AppData\Local\Autodesk\Revit\Autodesk Revit 2021\Journals
if not exist "%JOURNAL_DIR%" set JOURNAL_DIR=%USERPROFILE%\AppData\Local\Autodesk\Revit\Autodesk Revit 2022\Journals
if not exist "%JOURNAL_DIR%" set JOURNAL_DIR=%USERPROFILE%\AppData\Local\Autodesk\Revit\Autodesk Revit 2023\Journals
if not exist "%JOURNAL_DIR%" set JOURNAL_DIR=%USERPROFILE%\AppData\Local\Autodesk\Revit\Autodesk Revit 2024\Journals
if not exist "%JOURNAL_DIR%" set JOURNAL_DIR=%USERPROFILE%\AppData\Local\Autodesk\Revit\Autodesk Revit 2025\Journals
if not exist "%JOURNAL_DIR%" set JOURNAL_DIR=%USERPROFILE%\AppData\Local\Autodesk\Revit\Autodesk Revit 2026\Journals

echo Journal directory: %JOURNAL_DIR%
echo.

if exist "%JOURNAL_DIR%" (
    echo Searching recent journal files...
    echo.
    
    REM Search the most recent journal files
    for /f "delims=" %%f in ('dir /b /o-d "%JOURNAL_DIR%\*.txt" 2^>nul') do (
        echo Checking: %%f
        findstr /c:"REVBOT_TEST_SUCCESS" "%JOURNAL_DIR%\%%f" 2>nul
        if not errorlevel 1 (
            echo.
            echo ✅ FOUND TEST SUCCESS in %%f
            echo.
            echo Context around the success message:
            echo ========================================
            findstr /c:"REVBOT_TEST" "%JOURNAL_DIR%\%%f"
            echo ========================================
            goto :found
        )
    )
    
    echo ❌ REVBOT_TEST_SUCCESS not found in recent journal files
    echo.
    echo This means either:
    echo 1. The script didn't execute
    echo 2. The script executed but failed before the print
    echo 3. Looking in wrong journal directory
    
    :found
) else (
    echo ❌ Journal directory not found
    echo.
    echo Try manually searching for REVBOT_TEST_SUCCESS in:
    echo %USERPROFILE%\AppData\Local\Autodesk\Revit\
)

echo.
pause