from datetime import date, timedelta

from app import app
from extensions import db

from models.location import Panchayat
from models.panchayat_features import PanchayatFeature
from models.historical_weather import HistoricalWeather


# ============================================================
# DEMO PANCHAYAT FEATURES
# ============================================================

FEATURE_DATA = {

    "Example Panchayat 1": {
        "land_cover": "Mixed Agriculture",
        "water_proximity_km": 1.8,
        "terrain_type": "Low Hill / Valley",
        "historical_flood_susceptibility": 0.62,
        "vegetation_index": 0.71,
    },

    "Example Panchayat 2": {
        "land_cover": "Agriculture / Forest Edge",
        "water_proximity_km": 3.4,
        "terrain_type": "Rolling Terrain",
        "historical_flood_susceptibility": 0.38,
        "vegetation_index": 0.64,
    }
}


# ============================================================
# HISTORICAL DEMO WEATHER GENERATOR
# ============================================================

def generate_historical_data(
    panchayat,
    days=120
):

    existing = HistoricalWeather.query.filter_by(
        panchayat_id=panchayat.id
    ).count()

    if existing > 0:

        print(
            f"Historical data already exists: "
            f"{panchayat.name} ({existing} records)"
        )

        return

    base_temperature = 26.0

    base_humidity = 78.0

    base_wind = 12.0

    for i in range(days):

        observation_date = (
            date.today()
            - timedelta(days=i + 1)
        )

        # ----------------------------------------------------
        # Deterministic demo variation
        # ----------------------------------------------------

        temperature = (
            base_temperature
            + ((i * 7) % 9) * 0.35
            - 1.2
        )

        humidity = (
            base_humidity
            + ((i * 5) % 15)
            - 7
        )

        rainfall = (
            ((i * 11) % 30) / 10.0
        )

        wind = (
            base_wind
            + ((i * 3) % 12) * 0.6
        )

        pressure = (
            1007.0
            + ((i * 13) % 18) * 0.35
        )

        record = HistoricalWeather(

            panchayat_id=panchayat.id,

            observation_date=observation_date,

            temperature_c=round(
                temperature,
                2
            ),

            rainfall_mm=round(
                rainfall,
                2
            ),

            humidity_percent=round(
                humidity,
                2
            ),

            wind_speed_kmh=round(
                wind,
                2
            ),

            pressure_hpa=round(
                pressure,
                2
            ),

            source="DEMO_DATASET",

            data_type="SIMULATED"
        )

        db.session.add(record)


# ============================================================
# MAIN
# ============================================================

with app.app_context():

    panchayats = Panchayat.query.order_by(
        Panchayat.id
    ).all()

    if not panchayats:

        print(
            "No Panchayats found."
        )

        raise SystemExit(1)


    # --------------------------------------------------------
    # Panchayat features
    # --------------------------------------------------------

    for panchayat in panchayats:

        feature_data = FEATURE_DATA.get(
            panchayat.name
        )

        if not feature_data:

            print(
                f"No demo feature configuration for "
                f"{panchayat.name}"
            )

            continue


        feature = PanchayatFeature.query.filter_by(
            panchayat_id=panchayat.id
        ).first()


        if feature:

            print(
                f"Features already exist: "
                f"{panchayat.name}"
            )

        else:

            feature = PanchayatFeature(

                panchayat_id=panchayat.id,

                latitude=panchayat.latitude,

                longitude=panchayat.longitude,

                elevation_m=panchayat.elevation_m,

                land_cover=
                    feature_data["land_cover"],

                water_proximity_km=
                    feature_data["water_proximity_km"],

                terrain_type=
                    feature_data["terrain_type"],

                historical_flood_susceptibility=
                    feature_data[
                        "historical_flood_susceptibility"
                    ],

                vegetation_index=
                    feature_data[
                        "vegetation_index"
                    ],

                source="DEMO",

                data_type="SIMULATED"
            )

            db.session.add(feature)

            print(
                f"Created features: "
                f"{panchayat.name}"
            )


    # --------------------------------------------------------
    # Historical weather
    # --------------------------------------------------------

    for panchayat in panchayats:

        generate_historical_data(
            panchayat,
            days=120
        )


    db.session.commit()


print()
print("=" * 60)
print("MEGHDRISHTI ")
print("=" * 60)
print()