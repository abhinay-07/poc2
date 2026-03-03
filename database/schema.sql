-- ============================================
-- SODA_V3_PHASE1 - KYC Data Quality Monitoring
-- Database Schema
-- ============================================

-- Users table
CREATE TABLE IF NOT EXISTS users (
    user_id     SERIAL PRIMARY KEY,
    full_name   VARCHAR(100),
    email       VARCHAR(100),
    age         INT,
    country     VARCHAR(50),
    status      VARCHAR(20),
    created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- KYC Documents table
CREATE TABLE IF NOT EXISTS kyc_documents (
    doc_id      SERIAL PRIMARY KEY,
    user_id     INT REFERENCES users(user_id),
    doc_type    VARCHAR(50),
    verified    BOOLEAN,
    expiry_date DATE,
    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Scan Summary table
CREATE TABLE IF NOT EXISTS scan_summary (
    scan_id         SERIAL PRIMARY KEY,
    scan_timestamp  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    total_checks    INT,
    passed_checks   INT,
    failed_checks   INT
);

-- Check Results table
CREATE TABLE IF NOT EXISTS check_results (
    result_id       SERIAL PRIMARY KEY,
    scan_id         INT REFERENCES scan_summary(scan_id),
    table_name      VARCHAR(50),
    check_name      VARCHAR(200),
    status          VARCHAR(20),
    severity        VARCHAR(20),
    result_message  TEXT
);
