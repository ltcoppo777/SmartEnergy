@echo off
echo ========================================
echo Smart Energy Optimizer - Full System
echo ========================================
echo.
echo Starting:
echo - Backend API (port 8000)
echo - Frontend UI (port 5173)
echo - ML Agent Training
echo.
echo Press Ctrl+C to stop all services
echo ========================================
echo.

npm run start:with-train
