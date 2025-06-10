@echo off
REM pyRevit CLI debug test - shows more details

echo ========================================
echo pyRevit CLI Debug Test
echo ========================================
echo.

echo Running pyrevit run with --debug flag...
echo.
pyrevit run test_simple.py --debug

echo.
echo ========================================
echo.
echo If you see "Model does not exist", you need to:
echo 1. Open Revit 
echo 2. Create a new project (File ^> New ^> Project)
echo 3. Save the project
echo 4. Then run this test again
echo.
echo The script needs an active Revit document to execute!
echo ========================================
echo.
pause