@echo off
REM ============================================
REM SODA_V3_PHASE1 - Run Script
REM Runs the scanner then starts the dashboard
REM ============================================

echo ==========================================
echo  SODA_V3_PHASE1 - KYC Data Quality Monitor
echo ==========================================
echo.

set /p PGPORT="Enter PostgreSQL port (default 5432): "
if "%PGPORT%"=="" set PGPORT=5432

set POSTGRES_HOST=localhost
set POSTGRES_PORT=%PGPORT%
set POSTGRES_DB=kyc_db
set POSTGRES_USER=kyc_user
set POSTGRES_PASSWORD=kyc_pass

echo.
echo [1/2] Running Soda data quality scanner...
echo.
python data_quality/scanner.py

echo.
echo [2/2] Starting Streamlit dashboard...
echo       Open http://localhost:8501 in your browser
echo       Press Ctrl+C to stop
echo.
streamlit run app/dashboard.py --server.port=8501 --server.headless=true
