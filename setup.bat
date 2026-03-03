@echo off
REM ============================================
REM SODA_V3_PHASE1 - Database Setup Script
REM Run this ONCE to create the database
REM ============================================

echo ==========================================
echo  SODA_V3_PHASE1 - Database Setup
echo ==========================================
echo.

set /p PGPORT="Enter PostgreSQL port (default 5432): "
if "%PGPORT%"=="" set PGPORT=5432

echo.
echo [1/3] Creating user 'kyc_user'...
psql -U postgres -p %PGPORT% -c "CREATE USER kyc_user WITH PASSWORD 'kyc_pass';" 2>nul
if %errorlevel% neq 0 (
    echo       User may already exist - continuing...
)

echo [2/3] Creating database 'kyc_db'...
psql -U postgres -p %PGPORT% -c "CREATE DATABASE kyc_db OWNER kyc_user;" 2>nul
if %errorlevel% neq 0 (
    echo       Database may already exist - continuing...
)

echo [3/3] Loading schema and seed data...
psql -U kyc_user -d kyc_db -p %PGPORT% -f database/schema.sql
psql -U kyc_user -d kyc_db -p %PGPORT% -f database/seed_data.sql

echo.
echo ==========================================
echo  Setup complete!
echo  Run 'run.bat' to start the project.
echo ==========================================
pause
