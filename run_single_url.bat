@echo off
echo ===================================================
echo   Starting CompanyIQ on Single Localhost URL
echo   URL: http://localhost:8000
echo ===================================================
echo.

cd /d "%~dp0\companyiq\backend"
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
pause
