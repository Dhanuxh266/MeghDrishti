"""Notification delivery adapters for MeghDrishti notification service.

The default configuration is safe: no external SMS is sent until an SMS provider
and API key are explicitly configured. Fast2SMS Quick SMS is supported as an
optional provider for MVP testing/internal alerts. Production government SMS
should use the provider's approved DLT route/templates where required.
"""

import os
import re
from typing import Dict, Any

import requests


FAST2SMS_URL = "https://www.fast2sms.com/dev/bulkV2"


def normalize_indian_mobile(value: str | None) -> str | None:
    """Return a 10-digit Indian mobile number or None."""
    if not value:
        return None
    digits = re.sub(r"\D", "", str(value))
    if digits.startswith("91") and len(digits) == 12:
        digits = digits[2:]
    if len(digits) != 10 or not digits.startswith(("6", "7", "8", "9")):
        return None
    return digits


def build_sms_message(alert) -> str:
    """Build a compact alert message suitable for SMS transport."""
    score = f"{float(alert.risk_score):.1f}/100" if alert.risk_score is not None else "--"
    level = str(alert.severity or "ALERT").upper()
    panchayat = getattr(alert.panchayat, "name", "Panchayat")
    action = "Prepare locally" if level == "ORANGE" else "Priority attention" if level == "RED" else "Review locally"
    message = (
        f"MEGHDRISHTI: {level} screening alert for {panchayat}. "
        f"Risk {score}. {action}. Screening indicator, not an official IMD warning."
    )
    return message[:480]


def provider_status() -> Dict[str, Any]:
    provider = os.getenv("SMS_PROVIDER", "disabled").strip().lower()
    dry_run = os.getenv("SMS_DRY_RUN", "0").strip().lower() in {"1", "true", "yes", "on"}
    configured = provider == "fast2sms" and bool(os.getenv("FAST2SMS_API_KEY", "").strip())
    return {
        "provider": provider,
        "configured": configured,
        "dry_run": dry_run,
        "route": os.getenv("FAST2SMS_ROUTE", "q").strip().lower() or "q",
    }


def send_sms(mobile: str, message: str) -> Dict[str, Any]:
    """Send one SMS and return an honest provider result.

    No external request is made when SMS_DRY_RUN is enabled.
    """
    status = provider_status()
    number = normalize_indian_mobile(mobile)
    if not number:
        return {"success": False, "status": "FAILED", "error": "Invalid Indian mobile number."}

    if status["dry_run"]:
        return {
            "success": True,
            "status": "DRY_RUN",
            "provider": status["provider"],
            "message": "SMS delivery simulated; no external provider request was made.",
        }

    if status["provider"] != "fast2sms":
        return {"success": False, "status": "FAILED", "error": "SMS provider is not configured."}

    api_key = os.getenv("FAST2SMS_API_KEY", "").strip()
    if not api_key:
        return {"success": False, "status": "FAILED", "error": "FAST2SMS_API_KEY is not configured."}

    route = status["route"]
    if route not in {"q", "dlt"}:
        return {"success": False, "status": "FAILED", "error": "Unsupported Fast2SMS route. Use q or dlt."}

    payload = {
        "route": route,
        "numbers": number,
        "sms_details": "1",
    }

    if route == "q":
        payload["message"] = message
    else:
        # DLT requires an approved message/template configuration. Do not
        # silently invent one; require the configured message ID.
        dlt_message_id = os.getenv("FAST2SMS_DLT_MESSAGE_ID", "").strip()
        sender_id = os.getenv("FAST2SMS_SENDER_ID", "").strip()
        if not dlt_message_id or not sender_id:
            return {
                "success": False,
                "status": "FAILED",
                "error": "DLT route requires FAST2SMS_DLT_MESSAGE_ID and FAST2SMS_SENDER_ID.",
            }
        payload["message"] = dlt_message_id
        payload["sender_id"] = sender_id
        variables = os.getenv("FAST2SMS_DLT_VARIABLES", "").strip()
        if variables:
            payload["variables_values"] = variables

    try:
        response = requests.post(
            os.getenv("FAST2SMS_URL", FAST2SMS_URL),
            headers={
                "Authorization": api_key,
                "Content-Type": "application/json",
                "Accept": "application/json",
            },
            json=payload,
            timeout=20,
        )
        data = response.json() if response.content else {}
    except requests.RequestException as exc:
        return {"success": False, "status": "FAILED", "error": f"Provider request failed: {exc}"}
    except ValueError:
        data = {}

    provider_success = response.ok and data.get("return", True) is not False
    if not provider_success:
        provider_message = data.get("message") or data.get("error") or f"HTTP {response.status_code}"
        return {
            "success": False,
            "status": "FAILED",
            "error": str(provider_message),
            "http_status": response.status_code,
        }

    request_id = data.get("request_id")
    return {
        "success": True,
        "status": "ACCEPTED",
        "provider": "fast2sms",
        "request_id": request_id,
        "message": "Fast2SMS accepted the SMS request. Delivery status is not yet confirmed.",
        "http_status": response.status_code,
    }
