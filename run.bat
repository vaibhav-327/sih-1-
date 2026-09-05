@echo off
echo ========================================================
echo        MPLAD AI SENTINEL - QUICK LAUNCHER
echo ========================================================
echo.

echo [1/3] Verifying Python Environment & Seeding Database...
python scripts/seed_database.py
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Failed to seed database.
    pause
    exit /b %ERRORLEVEL%
)

echo.
echo [2/3] Starting FastAPI Backend on http://localhost:8000 ...
start "MPLAD AI Sentinel Backend" cmd /k "uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000"

echo.
echo [3/3] Starting React Frontend on http://localhost:5173 ...
cd frontend
start "MPLAD AI Sentinel Frontend" cmd /k "npm run dev"

echo.
echo ========================================================
echo   MPLAD AI SENTINEL IS RUNNING!
echo   * Backend API:  http://localhost:8000/docs
echo   * Frontend App: http://localhost:5173
echo ========================================================
echo.
pause
