"""Offline .

This suite deliberately makes no external network calls and does not require Flask.
It verifies the provider adapter, message construction, mobile normalization, and
source-level consistency of the .
"""

import os
from pathlib import Path

from services.notification_service import (
    build_sms_message,
    normalize_indian_mobile,
    provider_status,
    send_sms,
)

ROOT = Path(__file__).resolve().parents[1]
APP = (ROOT / "app.py").read_text(encoding="utf-8")
JS = (ROOT / "frontend/static/js/app.js").read_text(encoding="utf-8")


def check(condition, message):
    if not condition:
        raise AssertionError(message)


class DummyAlert:
    risk_score = 72.4
    severity = "ORANGE"

    class Panchayat:
        name = "Demo Panchayat"

    panchayat = Panchayat()


# Mobile normalization.
check(normalize_indian_mobile("+91 98765 43210") == "9876543210", "Indian +91 mobile normalization failed")
check(normalize_indian_mobile("9876543210") == "9876543210", "10-digit mobile normalization failed")
check(normalize_indian_mobile("12345") is None, "Invalid mobile should be rejected")

# Message safety/length.
message = build_sms_message(DummyAlert())
check(message.startswith("MEGHDRISHTI: ORANGE"), "SMS message prefix is incorrect")
check("not an official IMD warning" in message, "SMS disclaimer is missing")
check(len(message) <= 480, "SMS message exceeds adapter limit")

# Dry-run must never make a provider request.
os.environ["SMS_PROVIDER"] = "fast2sms"
os.environ["FAST2SMS_API_KEY"] = "test-key"
os.environ["SMS_DRY_RUN"] = "1"
result = send_sms("9876543210", message)
check(result["success"] is True and result["status"] == "DRY_RUN", "Dry-run SMS state is incorrect")

# Disabled provider must fail honestly.
os.environ["SMS_DRY_RUN"] = "0"
os.environ["SMS_PROVIDER"] = "disabled"
result = send_sms("9876543210", message)
check(result["success"] is False and result["status"] == "FAILED", "Disabled provider should fail safely")

# DLT route must not invent template/sender identifiers.
os.environ["SMS_PROVIDER"] = "fast2sms"
os.environ["FAST2SMS_ROUTE"] = "dlt"
os.environ.pop("FAST2SMS_DLT_MESSAGE_ID", None)
os.environ.pop("FAST2SMS_SENDER_ID", None)
result = send_sms("9876543210", message)
check(result["success"] is False and "DLT route requires" in result["error"], "DLT configuration guard failed")

# Source-level consistency checks for /notification state.
for token in [
    '/api/alerts',
    '/api/alerts/history',
    '/api/alerts/generate/',
    '/api/alerts/<int:alert_id>/acknowledge',
    '/api/alerts/<int:alert_id>/resolve',
    '/api/alerts/<int:alert_id>/send-sms',
    '/api/alerts/<int:alert_id>/notifications',
    'DRY_RUN',
    'SMS_READY',
]:
    check(token in APP, f"Missing : {token}")

for token in [
    'loadAlerts()',
    'loadAlertHistory()',
    'sendAlertSms',
    'updateAlertStatus',
    'dryRun',
]:
    check(token in JS, f"Missing : {token}")

print(": PASS")
print("External SMS calls made: 0")
