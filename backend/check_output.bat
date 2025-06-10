@echo off
REM Check the output from pyRevit file test

echo Checking for pyRevit output file...
echo.

set OUTPUT_FILE=%TEMP%\revbot_test_output.txt

if exist "%OUTPUT_FILE%" (
    echo ✅ Output file found!
    echo.
    echo Contents:
    echo ========================================
    type "%OUTPUT_FILE%"
    echo ========================================
    echo.
    echo Last modified: 
    dir "%OUTPUT_FILE%" | findstr /C:"revbot_test_output.txt"
) else (
    echo ❌ No output file found at %OUTPUT_FILE%
)

echo.
pause