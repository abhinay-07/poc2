"""
SODA_V3_PHASE1 - Scanner
Connects to PostgreSQL, runs Soda checks, and stores results.
"""

import os
import sys
import time
import psycopg2
from datetime import datetime

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
DB_HOST = os.getenv("POSTGRES_HOST", "localhost")
DB_PORT = os.getenv("POSTGRES_PORT", "5432")
DB_NAME = os.getenv("POSTGRES_DB", "kyc_db")
DB_USER = os.getenv("POSTGRES_USER", "kyc_user")
DB_PASS = os.getenv("POSTGRES_PASSWORD", "kyc_pass")

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CHECKS_FILE = os.getenv("SODA_CHECKS_FILE", os.path.join(SCRIPT_DIR, "soda_checks.yml"))


def wait_for_db(max_retries: int = 30, delay: int = 3) -> psycopg2.extensions.connection:
    """Wait until PostgreSQL is ready and seed data exists."""
    for attempt in range(1, max_retries + 1):
        try:
            conn = psycopg2.connect(
                host=DB_HOST, port=DB_PORT,
                dbname=DB_NAME, user=DB_USER, password=DB_PASS,
            )
            cur = conn.cursor()
            cur.execute("SELECT COUNT(*) FROM users")
            count = cur.fetchone()[0]
            cur.close()
            if count > 0:
                print(f"[scanner] DB ready – {count} users found.")
                return conn
            else:
                print(f"[scanner] DB up but no data yet (attempt {attempt}/{max_retries})")
                conn.close()
        except Exception as exc:
            print(f"[scanner] Waiting for DB (attempt {attempt}/{max_retries}): {exc}")
        time.sleep(delay)
    print("[scanner] Could not connect to database. Exiting.")
    sys.exit(1)


def run_soda_scan() -> list[dict]:
    """
    Run Soda Core scan and return parsed check results.
    Each result dict: {table, check, status, severity, message}
    """
    from soda.scan import Scan

    scan = Scan()
    scan.set_scan_definition_name("kyc_scan")
    scan.set_data_source_name("kyc_postgres")

    # Build inline data-source YAML
    ds_yaml = (
        f"data_source kyc_postgres:\n"
        f"  type: postgres\n"
        f"  host: {DB_HOST}\n"
        f"  port: \"{DB_PORT}\"\n"
        f"  username: {DB_USER}\n"
        f"  password: {DB_PASS}\n"
        f"  database: {DB_NAME}\n"
    )
    scan.add_configuration_yaml_str(ds_yaml)
    scan.add_sodacl_yaml_file(CHECKS_FILE)

    print("[scanner] Running Soda scan …")
    exit_code = scan.execute()
    print(f"[scanner] Scan finished – exit code {exit_code}")

    results = []

    def _extract_table(chk):
        """Best-effort table name extraction from a check object."""
        try:
            cfg = chk.check_cfg
            if hasattr(cfg, "source_configurations") and isinstance(cfg.source_configurations, dict):
                return cfg.source_configurations.get("table_name", getattr(cfg, "source_header", "unknown"))
            if hasattr(cfg, "source_header"):
                return cfg.source_header
        except Exception:
            pass
        return "unknown"

    def _extract_name(chk):
        """Best-effort check name extraction."""
        return chk.name if chk.name else str(getattr(chk, "check_cfg", chk))

    def _append_checks(check_list, status, severity, default_msg):
        for chk in check_list:
            results.append({
                "table": _extract_table(chk),
                "check": _extract_name(chk),
                "status": status,
                "severity": severity,
                "message": str(getattr(chk, "outcomes", default_msg)) or default_msg,
            })

    try:
        _append_checks(scan.get_checks_that_passed(), "PASS", "info", "Check passed")
        _append_checks(scan.get_checks_that_warned(), "WARN", "warning", "Warning")
        _append_checks(scan.get_checks_that_failed(), "FAIL", "critical", "Check failed")
    except AttributeError:
        print("[scanner] Public check accessors unavailable, falling back to internal API")

    # Fallback: parse all checks generically via internal API
    if not results and hasattr(scan, "_checks"):
        for chk in scan._checks:
            try:
                outcome = chk.outcome.value if hasattr(chk.outcome, "value") else str(chk.outcome)
            except Exception:
                outcome = "unknown"
            status_map = {"pass": "PASS", "fail": "FAIL", "warn": "WARN"}
            status = status_map.get(outcome.lower(), outcome.upper())
            results.append({
                "table": _extract_table(chk),
                "check": _extract_name(chk),
                "status": status,
                "severity": "critical" if status == "FAIL" else ("warning" if status == "WARN" else "info"),
                "message": f"Check {status.lower()}",
            })

    return results


def store_results(conn: psycopg2.extensions.connection, results: list[dict]) -> None:
    """Persist scan summary and individual check results."""
    total = len(results)
    passed = sum(1 for r in results if r["status"] == "PASS")
    failed = sum(1 for r in results if r["status"] == "FAIL")

    cur = conn.cursor()

    cur.execute(
        """
        INSERT INTO scan_summary (total_checks, passed_checks, failed_checks)
        VALUES (%s, %s, %s)
        RETURNING scan_id
        """,
        (total, passed, failed),
    )
    scan_id = cur.fetchone()[0]

    for r in results:
        cur.execute(
            """
            INSERT INTO check_results
                (scan_id, table_name, check_name, status, severity, result_message)
            VALUES (%s, %s, %s, %s, %s, %s)
            """,
            (scan_id, r["table"], r["check"], r["status"], r["severity"], r["message"]),
        )

    conn.commit()
    cur.close()
    print(f"[scanner] Stored scan {scan_id}: total={total} passed={passed} failed={failed}")


def main() -> None:
    conn = wait_for_db()
    try:
        results = run_soda_scan()
        store_results(conn, results)
    finally:
        conn.close()
    print("[scanner] Done.")


if __name__ == "__main__":
    main()
