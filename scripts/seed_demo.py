from werkzeug.security import generate_password_hash

from app import app
from extensions import db

from models.user import User
from models.location import (
    State,
    District,
    Taluka,
    Panchayat
)


def get_or_create(model, defaults=None, **kwargs):

    instance = model.query.filter_by(**kwargs).first()

    if instance:
        return instance

    instance = model(
        **kwargs,
        **(defaults or {})
    )

    db.session.add(instance)
    db.session.flush()

    return instance


with app.app_context():

    # =====================================================
    # LOCATION HIERARCHY
    # Demo structure for 
    # =====================================================

    state = get_or_create(
        State,
        name="Maharashtra"
    )

    district = get_or_create(
        District,
        name="Ratnagiri",
        state_id=state.id
    )

    taluka = get_or_create(
        Taluka,
        name="Chiplun",
        district_id=district.id
    )

    panchayat_1 = get_or_create(
        Panchayat,
        name="Example Panchayat 1",
        taluka_id=taluka.id,
        defaults={
            "latitude": 17.53,
            "longitude": 73.52,
            "elevation_m": 40,
            "population": 5000,
            "area_sq_km": 12.5
        }
    )

    panchayat_2 = get_or_create(
        Panchayat,
        name="Example Panchayat 2",
        taluka_id=taluka.id,
        defaults={
            "latitude": 17.56,
            "longitude": 73.55,
            "elevation_m": 65,
            "population": 4200,
            "area_sq_km": 10.8
        }
    )

    # =====================================================
    # DEMO USERS
    # =====================================================

    users = [
        {
            "name": "Government Administrator",
            "email": "gov@meghdrishti.local",
            "mobile": "9000000001",
            "password": "Gov@12345",
            "role": "government"
        },
        {
            "name": "Panchayat Official",
            "email": "panchayat@meghdrishti.local",
            "mobile": "9000000002",
            "password": "Panchayat@123",
            "role": "panchayat_official",
            "state_id": state.id,
            "district_id": district.id,
            "taluka_id": taluka.id,
            "panchayat_id": panchayat_1.id
        },
        {
            "name": "Citizen User",
            "email": "citizen@meghdrishti.local",
            "mobile": "9000000003",
            "password": "Citizen@123",
            "role": "citizen",
            "state_id": state.id,
            "district_id": district.id,
            "taluka_id": taluka.id,
            "panchayat_id": panchayat_1.id
        }
    ]

    for data in users:

        existing = User.query.filter_by(
            email=data["email"]
        ).first()

        if existing:

            print(
                f"User already exists: {data['email']}"
            )

            continue

        user = User(
            name=data["name"],
            email=data["email"],
            mobile=data["mobile"],
            password_hash=generate_password_hash(
                data["password"]
            ),
            role=data["role"],
            state_id=data.get("state_id"),
            district_id=data.get("district_id"),
            taluka_id=data.get("taluka_id"),
            panchayat_id=data.get("panchayat_id"),
            is_active=True
        )

        db.session.add(user)

        print(
            f"Created: {data['email']} "
            f"({data['role']})"
        )

    db.session.commit()

    print()
    print("=" * 55)
    print("MEGHDRISHTI ")
    print("=" * 55)
    print()
    print("Government:")
    print("  gov@meghdrishti.local")
    print("  Gov@12345")
    print()
    print("Panchayat Official:")
    print("  panchayat@meghdrishti.local")
    print("  Panchayat@123")
    print()
    print("Citizen:")
    print("  citizen@meghdrishti.local")
    print("  Citizen@123")
    print()