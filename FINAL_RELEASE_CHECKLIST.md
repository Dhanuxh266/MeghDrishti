# MEGHDRISHTI — Final SIH Release Checklist

## Release
- Source of truth: `meghdrishti_final(3).zip`
- Final build: Day 8F
- Runtime model: Random Forest
- Production database: persistent PostgreSQL required
- Local/demo database: SQLite supported
- Deployment tree target: below 500 MB

## Core demonstration
1. Government login
2. Select Panchayat
3. Current weather + forecast
4. AI downscaling prediction
5. Explainable risk score and map
6. Generate Orange/Red screening alert
7. Acknowledge response
8. Notification/SMS dry-run or configured provider handoff
9. Resolve alert
10. Panchayat Official login and scoped response view
11. Citizen login and localized safety view

## Scientific honesty
- Demo/simulated data is labelled as such.
- Risk bands are screening indicators, not official IMD warning thresholds.
- SMS `DRY_RUN` never means a real SMS was delivered.
- Provider acceptance is not equivalent to handset delivery.
- Production use requires validated meteorological, geographic and government datasets.

## Release checks
Run from the project root:

```bash
python -m compileall -q .
python scripts/test_day8_offline.py
python scripts/test_day8_demo.py
python scripts/test_day8e_deployment.py
python scripts/test_day8_demo.py
python scripts/test_ai_offline.py
python scripts/test_risk.py
python scripts/test_notifications.py
python scripts/check_release_size.py
```

For live deployment, install `requirements.txt`, configure a strong `SECRET_KEY`, a persistent PostgreSQL `DATABASE_URL`, and provider credentials only through the host's environment settings.
