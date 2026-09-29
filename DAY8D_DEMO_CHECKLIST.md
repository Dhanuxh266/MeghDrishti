# Day 8D — Demo Verification Checklist

This checklist is designed for the final SIH demonstration. It is intentionally offline-safe: verification does not call the weather provider or SMS provider.

## Demo accounts

| Role | Email | Password | Scope |
|---|---|---|---|
| Government | `gov@meghdrishti.local` | `Gov@12345` | All demo Panchayats |
| Panchayat Official | `panchayat@meghdrishti.local` | `Panchayat@123` | Example Panchayat 1 |
| Citizen | `citizen@meghdrishti.local` | `Citizen@123` | Example Panchayat 1 |

These are demonstration credentials only. Change/remove them before a public production deployment.

## Recommended live demo sequence

1. Sign in as **Government**.
2. Select a Panchayat from the location hierarchy.
3. Verify current weather and forecast update.
4. Generate/view the AI Panchayat prediction.
5. Verify the explainable risk level and reason.
6. Open the risk map and confirm the selected Panchayat.
7. If the selected risk is ORANGE/RED, generate a screening alert.
8. Verify the alert appears in Active Alerts and Alert History.
9. Acknowledge the alert with an operational note.
10. Verify the acknowledgement appears in the response/history view.
11. Demonstrate SMS using **dry-run** unless a real, authorized provider configuration is available.
12. Resolve the alert and verify the history lifecycle.
13. Sign in as **Panchayat Official** and verify only the assigned Panchayat is operationally accessible.
14. Sign in as **Citizen** and verify the local weather/risk/safety view is read-only for alert operations.

## Scientific honesty

- Demo/simulated data must remain labelled as such.
- Risk is a screening indicator, not an official IMD warning threshold.
- SMS `DRY_RUN` means no message was sent.
- Provider acceptance is not the same as handset delivery.
