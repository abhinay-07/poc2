# SODA_V3_PHASE1 — KYC Data Quality Monitoring

A Docker-based platform that uses **Soda Core** to validate KYC data stored in **PostgreSQL** and presents results on a live **Streamlit** dashboard.

---

## Architecture

```
SODA_V3_PHASE1/
├── app/                  # Streamlit dashboard
│   ├── Dockerfile
│   ├── dashboard.py
│   └── requirements.txt
├── data_quality/         # Soda scanner
│   ├── Dockerfile
│   ├── scanner.py
│   ├── soda_checks.yml
│   └── requirements.txt
├── database/             # SQL init scripts
│   ├── schema.sql
│   └── seed_data.sql
├── docker-compose.yml
└── README.md
```

## Services

| Service              | Description                                    | Port  |
|----------------------|------------------------------------------------|-------|
| `postgres`           | PostgreSQL 16 with auto-created schema & seed  | 5432  |
| `soda_scanner`       | One-shot Soda scan at startup                  | —     |
| `soda_scheduler`     | Re-runs Soda scan every 6 hours                | —     |
| `streamlit_dashboard`| Live monitoring UI                             | 8501  |

## Quick Start

```bash
cd SODA_V3_PHASE1
docker compose up --build
```

Open the dashboard at **http://localhost:8501**

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

```bash
docker compose down
```

To also remove the database volume:

```bash
docker compose down -v
```
