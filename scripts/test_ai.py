import os
import sys
import json

# ============================================================
# PROJECT ROOT
# ============================================================

PROJECT_ROOT = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)


# ============================================================
# APPLICATION
# ============================================================

from app import app
from extensions import db
from models.user import User


# ============================================================
# TEST
# ============================================================

with app.app_context():

    print("=" * 70)
    print("MEGHDRISHTI — ")
    print("=" * 70)

    # --------------------------------------------------------
    # Find a government user
    # --------------------------------------------------------

    user = (
        User.query
        .filter_by(role="government")
        .first()
    )

    if not user:

        print()
        print("ERROR: No government user found.")
        print("Run the .")
        sys.exit(1)

    print()
    print("Test user:")
    print(f"  ID   : {user.id}")
    print(f"  Name : {user.name}")
    print(f"  Role : {user.role}")

    # --------------------------------------------------------
    # Flask test client
    # --------------------------------------------------------

    client = app.test_client()

    # --------------------------------------------------------
    # Create authenticated session
    # --------------------------------------------------------

    with client.session_transaction() as session:

        session["user_id"] = user.id
        session["role"] = user.role

    print()
    print("Authentication session: OK")

    # ========================================================
    # TEST 1 — POST AI PREDICTION
    # ========================================================

    print()
    print("-" * 70)
    print("TEST 1: POST AI PANCHAYAT PREDICTION")
    print("-" * 70)

    response = client.post(
        "/api/ai/panchayat/1/predict"
    )

    print()
    print("HTTP STATUS:", response.status_code)

    try:

        prediction_response = response.get_json()

        print(
            json.dumps(
                prediction_response,
                indent=2,
                default=str
            )
        )

    except Exception:

        print(
            response.get_data(
                as_text=True
            )
        )

        prediction_response = None

    if response.status_code != 200:

        print()
        print("AI PREDICTION TEST FAILED.")
        sys.exit(1)

    if not prediction_response:

        print()
        print("ERROR: Empty response.")
        sys.exit(1)

    if not prediction_response.get(
        "success"
    ):

        print()
        print("ERROR: API returned success=false.")
        sys.exit(1)

    print()
    print("AI prediction endpoint: PASSED")

    # ========================================================
    # TEST 2 — GET PREDICTION HISTORY
    # ========================================================

    print()
    print("-" * 70)
    print("TEST 2: GET AI PREDICTION HISTORY")
    print("-" * 70)

    response = client.get(
        "/api/ai/panchayat/1/predictions"
    )

    print()
    print("HTTP STATUS:", response.status_code)

    try:

        history_response = response.get_json()

        print(
            json.dumps(
                history_response,
                indent=2,
                default=str
            )
        )

    except Exception:

        print(
            response.get_data(
                as_text=True
            )
        )

        history_response = None

    if response.status_code != 200:

        print()
        print("PREDICTION HISTORY TEST FAILED.")
        sys.exit(1)

    if not history_response:

        print()
        print("ERROR: Empty history response.")
        sys.exit(1)

    print()
    print("Prediction history endpoint: PASSED")

    # ========================================================
    # FINAL RESULT
    # ========================================================

    print()
    print("=" * 70)
    print("")
    print("=" * 70)
    print()
    print("POST prediction endpoint : PASSED")
    print("GET prediction history   : PASSED")
    print()

    print(
        "Stored predictions:",
        history_response.get(
            "count",
            "unknown"
        )
    )

    print()
    print("=" * 70)