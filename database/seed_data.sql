-- ============================================
-- SODA_V3_PHASE1 - Seed Data
-- Includes valid, duplicate, underage,
-- invalid email, missing KYC, expired docs
-- ============================================

-- =====================
-- USERS
-- =====================

-- Valid users
INSERT INTO users (full_name, email, age, country, status) VALUES
('Rahul Sharma',    'rahul.sharma@gmail.com',     32, 'India',   'ACTIVE'),
('Emily Johnson',   'emily.johnson@outlook.com',  28, 'USA',     'ACTIVE'),
('Hans Mueller',    'hans.mueller@web.de',         45, 'Germany', 'ACTIVE'),
('James Smith',     'james.smith@yahoo.co.uk',     37, 'UK',      'ACTIVE'),
('Priya Patel',     'priya.patel@hotmail.com',     29, 'India',   'ACTIVE'),
('Sarah Williams',  'sarah.williams@gmail.com',    41, 'USA',     'INACTIVE'),
('Oliver Brown',    'oliver.brown@gmail.com',      33, 'UK',      'ACTIVE'),
('Anna Schmidt',    'anna.schmidt@gmx.de',         26, 'Germany', 'ACTIVE');

-- Duplicate emails (same email as existing users)
INSERT INTO users (full_name, email, age, country, status) VALUES
('Rahul Kumar',     'rahul.sharma@gmail.com',      30, 'India',   'ACTIVE'),
('Emily J. Clone',  'emily.johnson@outlook.com',   25, 'USA',     'ACTIVE');

-- Underage users (age < 18)
INSERT INTO users (full_name, email, age, country, status) VALUES
('Tom Young',       'tom.young@gmail.com',          15, 'UK',      'ACTIVE'),
('Lisa Minor',      'lisa.minor@yahoo.com',         12, 'USA',     'ACTIVE'),
('Arjun Kid',       'arjun.kid@hotmail.com',        16, 'India',   'ACTIVE');

-- Invalid email formats
INSERT INTO users (full_name, email, age, country, status) VALUES
('Bad Email One',   'bademail-no-at.com',           30, 'Germany', 'ACTIVE'),
('Bad Email Two',   'another@bad@email.com',        27, 'USA',     'ACTIVE'),
('No Email User',   '',                             35, 'India',   'ACTIVE');

-- Users who will NOT have KYC documents (IDs 17, 18)
INSERT INTO users (full_name, email, age, country, status) VALUES
('Ghost User One',  'ghost1@email.com',             40, 'UK',      'ACTIVE'),
('Ghost User Two',  'ghost2@email.com',             38, 'Germany', 'INACTIVE');

-- =====================
-- KYC DOCUMENTS
-- =====================

-- Valid verified documents (for users 1-8)
INSERT INTO kyc_documents (user_id, doc_type, verified, expiry_date) VALUES
(1, 'PASSPORT',        TRUE,  '2028-06-15'),
(2, 'DRIVERS_LICENSE',  TRUE,  '2027-09-20'),
(3, 'NATIONAL_ID',      TRUE,  '2029-01-10'),
(4, 'PASSPORT',         TRUE,  '2027-12-31'),
(5, 'VOTERS_ID',        TRUE,  '2028-03-25'),
(6, 'PASSPORT',         TRUE,  '2027-08-14'),
(7, 'DRIVERS_LICENSE',  TRUE,  '2028-11-05'),
(8, 'NATIONAL_ID',      TRUE,  '2029-05-18');

-- Unverified documents
INSERT INTO kyc_documents (user_id, doc_type, verified, expiry_date) VALUES
(9,  'PASSPORT',        FALSE, '2027-04-10'),
(10, 'DRIVERS_LICENSE',  FALSE, '2028-02-28');

-- Expired documents
INSERT INTO kyc_documents (user_id, doc_type, verified, expiry_date) VALUES
(11, 'PASSPORT',        TRUE,  '2023-01-15'),
(12, 'NATIONAL_ID',     TRUE,  '2022-06-30'),
(13, 'VOTERS_ID',       FALSE, '2024-12-01'),
(14, 'DRIVERS_LICENSE',  TRUE,  '2021-09-10'),
(15, 'PASSPORT',        FALSE, '2020-03-20');

-- Note: users 16 (No Email User), 17 (Ghost User One), 18 (Ghost User Two) have NO documents
