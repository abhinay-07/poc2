# SODA_V3_PHASE1 — KYC Data Quality Monitoring

A platform that uses **Soda Core** to validate KYC data stored in **PostgreSQL** and presents results on a live **Streamlit** dashboard.

---

## Architecture

```
SODA_V3_PHASE1/
├── app/
│   └── dashboard.py          # Streamlit dashboard
├── data_quality/
│   ├── scanner.py            # Soda scanner
│   └── soda_checks.yml       # Soda check definitions
├── database/
│   ├── schema.sql            # Database schema
│   └── seed_data.sql         # Sample test data
├── requirements.txt          # All Python dependencies
├── setup.bat                 # One-click database setup (Windows)
├── run.bat                   # One-click run script (Windows)
└── README.md
```

## Prerequisites

| Tool | Version | Check Command |
|------|---------|---------------|
| **Python** | 3.11+ | `python --version` |
| **PostgreSQL** | 15+ | `psql --version` |
| **Git** | Any | `git --version` |

---

## Setup (One-Time)

### Step 1: Clone the repository

```powershell
git clone https://github.com/abhinay-07/poc2.git
cd poc2/SODA_V3_PHASE1
```

### Step 2: Install Python packages

```powershell
pip install -r requirements.txt
```

### Step 3: Create the database

**Option A — Run the setup script (Windows):**
```powershell
.\setup.bat
```

**Option B — Manual setup:**
```powershell
psql -U postgres
```
```sql
CREATE USER kyc_user WITH PASSWORD 'kyc_pass';
CREATE DATABASE kyc_db OWNER kyc_user;
\q
```
```powershell
psql -U kyc_user -d kyc_db -f database/schema.sql
psql -U kyc_user -d kyc_db -f database/seed_data.sql
```

> **Note:** If PostgreSQL runs on a different port (e.g., 5433), add `-p 5433` to all `psql` commands.

---

## Running the Project

**Option A — Run script (Windows):**
```powershell
.\run.bat
```

**Option B — Manual:**
```powershell
# Terminal 1: Run the Soda data quality scanner
python data_quality/scanner.py

# Terminal 2: Start the Streamlit dashboard
streamlit run app/dashboard.py --server.port=8501
```

Open the dashboard at **http://localhost:8501**

---

## Configuration (Environment Variables)

All settings have sensible defaults. Override only if your setup differs:

| Variable | Default | Description |
|----------|---------|-------------|
| `POSTGRES_HOST` | `localhost` | Database host |
| `POSTGRES_PORT` | `5432` | Database port |
| `POSTGRES_DB` | `kyc_db` | Database name |
| `POSTGRES_USER` | `kyc_user` | Database user |
| `POSTGRES_PASSWORD` | `kyc_pass` | Database password |

Example (PowerShell):
```powershell
$env:POSTGRES_PORT = "5433"
python data_quality/scanner.py
```

---

## Data Quality Checks

### Users Table
- `user_id` not null
- No duplicate `user_id`
- `age >= 18`
- Valid email format (regex)
- `country` in (`India`, `USA`, `UK`, `Germany`)
- `status` in (`ACTIVE`, `INACTIVE`)

### KYC Documents Table
- `user_id` references an existing user
- `verified = true`
- `expiry_date` is in the future

## Seed Data Scenarios

The seed data intentionally includes violations for testing:

| Scenario               | Details                        |
|------------------------|--------------------------------|
| Duplicate emails       | 2 users share emails           |
| Underage users         | 3 users with age < 18          |
| Invalid emails         | Empty / malformed addresses    |
| Missing KYC documents  | 3 users with no documents      |
| Expired documents      | 5 documents with past dates    |
| Unverified documents   | 2 documents not yet verified   |

## Stopping

Press `Ctrl+C` in the terminal running Streamlit to stop the dashboard.
