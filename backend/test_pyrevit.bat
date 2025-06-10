@echo off
REM Simple pyRevit CLI test script for Windows

echo ========================================
echo pyRevit CLI Test Suite
echo ========================================
echo.

REM Test 1: Check if pyRevit CLI is installed
echo [Test 1] Checking pyRevit CLI installation...
pyrevit --version
if errorlevel 1 (
    echo ❌ FAILED: pyRevit CLI not found or not in PATH
    echo    Please install pyRevit or add to PATH
    pause
    exit /b 1
) else (
    echo ✅ PASSED: pyRevit CLI found
)
echo.

REM Test 2: Check pyRevit environment
echo [Test 2] Checking pyRevit environment...
pyrevit env
echo.

REM Test 3: Check attached Revit instances
echo [Test 3] Checking for attached Revit instances...
pyrevit attached
echo.

REM Test 4: Run the simplest possible script
echo [Test 4] Running simple test script...
echo Creating test_simple.py if it doesn't exist...
if not exist test_simple.py (
    echo print("Hello from pyRevit!"^) > test_simple.py
    echo print("If you see this, pyRevit execution is working!"^) >> test_simple.py
)

echo.
echo Attempting to run test_simple.py...
pyrevit run test_simple.py
if errorlevel 1 (
    echo ❌ FAILED: Could not execute script
    echo.
    echo Common issues:
    echo 1. No Revit instance running
    echo 2. No document open in Revit
    echo 3. pyRevit not loaded in Revit
    echo 4. pyRevit CLI can't connect to Revit
) else (
    echo ✅ PASSED: Script executed successfully
)

echo.
echo ========================================
echo Test Summary:
echo ========================================
echo If Test 4 failed, ensure:
echo 1. Revit is running
echo 2. A project/document is open in Revit
echo 3. pyRevit tab is visible in Revit ribbon
echo 4. Try: pyrevit attach [revit_version] [revit_year]
echo.
pause