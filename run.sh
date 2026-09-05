#!/bin/bash
set -e

echo "========================================================"
echo "       MPLAD AI SENTINEL - QUICK LAUNCHER"
echo "========================================================"
echo ""

echo "[1/3] Verifying Python Environment & Seeding Database..."
python3 scripts/seed_database.py

echo ""
echo "[2/3] Starting FastAPI Backend on http://localhost:8000 ..."
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!

echo ""
echo "[3/3] Starting React Frontend on http://localhost:5173 ..."
cd frontend && npm run dev &
FRONTEND_PID=$!

echo ""
echo "========================================================"
echo "  MPLAD AI SENTINEL IS RUNNING!"
echo "  * Backend API:  http://localhost:8000/docs"
echo "  * Frontend App: http://localhost:5173"
echo "========================================================"
echo "Press CTRL+C to terminate both servers."

trap "kill $BACKEND_PID $FRONTEND_PID; exit" INT
wait
