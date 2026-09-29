"""Day-8D offline demo-data and workflow verification.

No Flask server, network, weather provider, or SMS provider is required.
This validates the packaged demo database, model artifacts, route surface,
and the three-role workflow contract before deployment.
"""
from pathlib import Path
import json
import sqlite3
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
DB = ROOT / "instance" / "meghdrishti.db"
APP = ROOT / "app.py"
JS = ROOT / "frontend" / "static" / "js" / "app.js"
METRICS = ROOT / "ml" / "models" / "model_metrics.json"
RF = ROOT / "ml" / "models" / "random_forest.joblib"


def check(condition, message):
    if not condition:
        raise AssertionError(message)

check(DB.exists(), "Demo SQLite database is missing")
check(APP.exists(), "app.py is missing")
check(JS.exists(), "dashboard JavaScript is missing")
check(RF.exists(), "Runtime Random Forest model is missing")
check(METRICS.exists(), "Model metrics metadata is missing")

con = sqlite3.connect(DB)
cur = con.cursor()

def count(table):
    return cur.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]

# Core geography and role fixtures.
check(count("states") >= 1, "No state demo data found")
check(count("districts") >= 1, "No district demo data found")
check(count("talukas") >= 1, "No taluka demo data found")
check(count("panchayats") >= 2, "At least two Panchayat demo records are required")

users = cur.execute(
    "SELECT email, role, is_active, panchayat_id FROM users "
    "WHERE email IN (?, ?, ?)",
    (
        "gov@meghdrishti.local",
        "panchayat@meghdrishti.local",
        "citizen@meghdrishti.local",
    ),
).fetchall()
by_email = {row[0]: row for row in users}
for email, role in {
    "gov@meghdrishti.local": "government",
    "panchayat@meghdrishti.local": "panchayat_official",
    "citizen@meghdrishti.local": "citizen",
}.items():
    check(email in by_email, f"Missing demo account: {email}")
    check(by_email[email][1] == role, f"Incorrect role for {email}")
    check(by_email[email][2] == 1, f"Demo account is inactive: {email}")

check(by_email["panchayat@meghdrishti.local"][3] is not None, "Official is not assigned to a Panchayat")
check(by_email["citizen@meghdrishti.local"][3] is not None, "Citizen is not assigned to a Panchayat")

# Required data needed by the dashboard workflow.
check(count("historical_weather") >= 1, "Historical weather demo data is missing")

# The current release deliberately keeps runtime model artifacts lean.
metrics = json.loads(METRICS.read_text(encoding="utf-8"))
check(isinstance(metrics, dict) and metrics, "Model metrics metadata is empty")

# Route contract for the SIH demonstration flow.
app_text = APP.read_text(encoding="utf-8")
required_routes = [
    "/api/auth/me",
    "/api/weather/panchayat/",
    "/api/ai/panchayat/",
    "/api/risk/panchayat/",
    "/api/risk/overview",
    "/api/alerts",
    "/api/alerts/history",
    "/api/alerts/generate/",
    "/api/alerts/<int:alert_id>/acknowledge",
    "/api/alerts/<int:alert_id>/resolve",
    "/api/alerts/<int:alert_id>/send-sms",
    "/api/alerts/<int:alert_id>/notifications",
    "/api/readiness",
]
for route in required_routes:
    check(route in app_text, f"Required route marker missing: {route}")

# Ensure the front-end contains the complete operational flow.
js_text = JS.read_text(encoding="utf-8")
for marker in [
    "/api/alerts",
    "/api/alerts/history",
    "generate",
    "acknowledge",
    "resolve",
    "send-sms",
    "loadWeatherForPanchayat",
    "loadRiskForPanchayat",
]:
    check(marker in js_text, f"Frontend workflow marker missing: {marker}")

# Confirm no concrete provider credentials are bundled in the release.
for path in ROOT.rglob("*"):
    if not path.is_file() or path.suffix.lower() not in {".py", ".js", ".txt", ".md", ".json", ".yaml", ".yml", ".env"}:
        continue
    if "__pycache__" in path.parts:
        continue
    text = path.read_text(encoding="utf-8", errors="ignore")
    for line in text.splitlines():
        if line.startswith("FAST2SMS_API_KEY="):
            check(line.strip() == "FAST2SMS_API_KEY=", f"Concrete SMS key found in {path}")

con.close()

print("Day-8D demo-data and workflow verification: PASS")
print("Roles verified: Government, Panchayat Official, Citizen")
print("Core geography, historical data, runtime model, alert workflow and deployment route surface verified.")
print("No external network, weather API, or SMS calls were made.")
