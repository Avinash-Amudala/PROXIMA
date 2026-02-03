@echo off
echo ========================================
echo Starting PROXIMA Backend API
echo ========================================
echo.
echo API will be available at:
echo   - http://localhost:8000
echo   - API Docs: http://localhost:8000/docs
echo.
echo Press Ctrl+C to stop the server
echo ========================================
echo.

cd src
py -m uvicorn proxima.api.main:app --reload --host 0.0.0.0 --port 8000

