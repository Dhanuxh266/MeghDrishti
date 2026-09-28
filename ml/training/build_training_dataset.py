import os
import sys

import numpy as np
import pandas as pd

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
sys.path.insert(0, PROJECT_ROOT)

from app import app
from models.location import Panchayat
from models.panchayat_features import PanchayatFeature
from models.historical_weather import HistoricalWeather

OUTPUT_DIR = os.path.join(PROJECT_ROOT, "data", "training")
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "meghdrishti_training_dataset.csv")


def build_dataset():
    rows = []

    with app.app_context():
        panchayats = Panchayat.query.all()
        if not panchayats:
            raise RuntimeError("No Panchayats found in database.")

        for panchayat in panchayats:
            feature = PanchayatFeature.query.filter_by(
                panchayat_id=panchayat.id
            ).first()
            if not feature:
                print(f"Skipping {panchayat.name}: features unavailable.")
                continue

            records = (
                HistoricalWeather.query
                .filter_by(panchayat_id=panchayat.id)
                .order_by(HistoricalWeather.observation_date.asc())
                .all()
            )

            for record in records:
                rows.append({
                    "panchayat_id": panchayat.id,
                    "panchayat_name": panchayat.name,
                    "date": record.observation_date,
                    "target_temperature_c": record.temperature_c,
                    "target_rainfall_mm": record.rainfall_mm,
                    "target_humidity_percent": record.humidity_percent,
                    "target_wind_speed_kmh": record.wind_speed_kmh,
                    "latitude": feature.latitude,
                    "longitude": feature.longitude,
                    "elevation_m": feature.elevation_m,
                    "water_proximity_km": feature.water_proximity_km,
                    "historical_flood_susceptibility": feature.historical_flood_susceptibility,
                    "vegetation_index": feature.vegetation_index,
                    "land_cover": feature.land_cover,
                    "terrain_type": feature.terrain_type,
                    "pressure_hpa": record.pressure_hpa,
                })

    raw = pd.DataFrame(rows)
    if raw.empty:
        raise RuntimeError("Training dataset is empty.")

    raw["date"] = pd.to_datetime(raw["date"])
    raw = raw.sort_values(["panchayat_id", "date"]).reset_index(drop=True)

    # ------------------------------------------------------------
    # TEMPORAL INTEGRITY
    # ------------------------------------------------------------
    # Target at date t may only use information available before t.
    # Coarse field = aggregate weather from t-1.
    # Historical features = local Panchayat weather from t-1.
    # Previous features = local Panchayat weather from t-2.
    # ------------------------------------------------------------

    daily_coarse = (
        raw.groupby("date")
        .agg(
            coarse_temperature_c=("target_temperature_c", "mean"),
            coarse_rainfall_mm=("target_rainfall_mm", "mean"),
            coarse_humidity_percent=("target_humidity_percent", "mean"),
            coarse_wind_speed_kmh=("target_wind_speed_kmh", "mean"),
        )
        .sort_index()
    )

    daily_coarse_prev = daily_coarse.shift(1).reset_index()

    local_history = raw[[
        "panchayat_id",
        "date",
        "target_temperature_c",
        "target_rainfall_mm",
        "target_humidity_percent",
        "target_wind_speed_kmh",
        "pressure_hpa",
    ]].copy()

    local_history = local_history.rename(columns={
        "date": "history_date",
        "target_temperature_c": "historical_temperature_c",
        "target_rainfall_mm": "historical_rainfall_mm",
        "target_humidity_percent": "historical_humidity_percent",
        "target_wind_speed_kmh": "historical_wind_speed_kmh",
        "pressure_hpa": "historical_pressure_hpa",
    })

    previous_history = local_history.rename(columns={
        "history_date": "previous_date",
        "historical_temperature_c": "previous_temperature_c",
        "historical_rainfall_mm": "previous_rainfall_mm",
        "historical_humidity_percent": "previous_humidity_percent",
        "historical_wind_speed_kmh": "previous_wind_speed_kmh",
        "historical_pressure_hpa": "previous_pressure_hpa",
    })

    # Match t with local t-1 by shifting the join key forward one day.
    local_history["date"] = local_history["history_date"] + pd.Timedelta(days=1)
    previous_history["date"] = previous_history["previous_date"] + pd.Timedelta(days=2)

    df = raw.merge(daily_coarse_prev, on="date", how="left")
    df = df.merge(
        local_history[[
            "panchayat_id", "date", "historical_temperature_c",
            "historical_rainfall_mm", "historical_humidity_percent",
            "historical_wind_speed_kmh", "historical_pressure_hpa",
        ]],
        on=["panchayat_id", "date"],
        how="left",
    )
    df = df.merge(
        previous_history[[
            "panchayat_id", "date", "previous_temperature_c",
            "previous_rainfall_mm", "previous_humidity_percent",
        ]],
        on=["panchayat_id", "date"],
        how="left",
    )

    df["month"] = df["date"].dt.month
    df["day_of_year"] = df["date"].dt.dayofyear

    # No row is retained unless all weather inputs come from dates before t.
    required = [
        "coarse_temperature_c",
        "coarse_rainfall_mm",
        "coarse_humidity_percent",
        "coarse_wind_speed_kmh",
        "historical_temperature_c",
        "historical_rainfall_mm",
        "historical_humidity_percent",
        "historical_wind_speed_kmh",
        "historical_pressure_hpa",
        "previous_temperature_c",
        "previous_rainfall_mm",
        "previous_humidity_percent",
    ]
    df = df.dropna(subset=required).reset_index(drop=True)

    df["dataset_type"] = "SIMULATED_DEMO_TRAINING"
    df["weather_source"] = "DEMO_DATASET"
    df["coarse_field_method"] = "PREVIOUS_DAY_CROSS_PANCHAYAT_MEAN"
    df["feature_temporal_rule"] = "TARGET_T_USES_ONLY_INFORMATION_FROM_T_MINUS_1_OR_EARLIER"

    # Sanity checks against the exact leakage that existed previously.
    if np.isclose(
        df["target_temperature_c"].to_numpy(),
        df["coarse_temperature_c"].to_numpy(),
        atol=1e-12,
    ).all():
        print("WARNING: coarse temperature equals target for every row; inspect demo data.")

    if np.isclose(
        df["target_temperature_c"].to_numpy(),
        df["historical_temperature_c"].to_numpy(),
        atol=1e-12,
    ).all():
        raise RuntimeError("Target leakage detected: historical temperature equals target.")

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    df.to_csv(OUTPUT_FILE, index=False)

    print("=" * 70)
    print("MEGHDRISHTI — TRAINING DATASET")
    print("=" * 70)
    print(f"Records: {len(df)}")
    print(f"Panchayats: {df['panchayat_id'].nunique()}")
    print(f"Date range: {df['date'].min().date()} -> {df['date'].max().date()}")
    print(f"Dataset type: {df['dataset_type'].iloc[0]}")
    print(f"Coarse field: {df['coarse_field_method'].iloc[0]}")
    print(f"Temporal rule: {df['feature_temporal_rule'].iloc[0]}")
    print(f"Output: {OUTPUT_FILE}")
    print("=" * 70)


if __name__ == "__main__":
    build_dataset()
