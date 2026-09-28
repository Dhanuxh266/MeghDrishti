import pandas as pd

from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder


# ============================================================
# INPUT FEATURES
# ============================================================

FEATURE_COLUMNS = [

    # Coarse weather
    "coarse_temperature_c",
    "coarse_rainfall_mm",
    "coarse_humidity_percent",
    "coarse_wind_speed_kmh",

    # Panchayat geography
    "latitude",
    "longitude",
    "elevation_m",
    "water_proximity_km",
    "historical_flood_susceptibility",
    "vegetation_index",

    # Historical weather
    "historical_temperature_c",
    "historical_rainfall_mm",
    "historical_humidity_percent",
    "historical_wind_speed_kmh",
    "historical_pressure_hpa",

    # Temporal
    "month",
    "day_of_year",

    # Lag
    "previous_temperature_c",
    "previous_rainfall_mm",
    "previous_humidity_percent",

    # Categorical
    "land_cover",
    "terrain_type"
]


TARGET_COLUMNS = [

    "target_temperature_c",
    "target_rainfall_mm",
    "target_humidity_percent",
    "target_wind_speed_kmh"
]


NUMERIC_FEATURES = [

    "coarse_temperature_c",
    "coarse_rainfall_mm",
    "coarse_humidity_percent",
    "coarse_wind_speed_kmh",

    "latitude",
    "longitude",
    "elevation_m",
    "water_proximity_km",

    "historical_flood_susceptibility",
    "vegetation_index",

    "historical_temperature_c",
    "historical_rainfall_mm",
    "historical_humidity_percent",
    "historical_wind_speed_kmh",
    "historical_pressure_hpa",

    "month",
    "day_of_year",

    "previous_temperature_c",
    "previous_rainfall_mm",
    "previous_humidity_percent"
]


CATEGORICAL_FEATURES = [
    "land_cover",
    "terrain_type"
]


# ============================================================
# PREPROCESSOR
# ============================================================

def create_preprocessor():

    return ColumnTransformer(

        transformers=[

            (
                "numeric",
                "passthrough",
                NUMERIC_FEATURES
            ),

            (
                "categorical",
                OneHotEncoder(
                    handle_unknown="ignore"
                ),
                CATEGORICAL_FEATURES
            )

        ],

        remainder="drop"
    )


# ============================================================
# LOAD TRAINING DATA
# ============================================================

def load_training_data(
    path
):

    df = pd.read_csv(
        path
    )


    missing_features = [
        col
        for col in FEATURE_COLUMNS
        if col not in df.columns
    ]


    missing_targets = [
        col
        for col in TARGET_COLUMNS
        if col not in df.columns
    ]


    if missing_features:

        raise ValueError(
            "Missing feature columns: "
            + ", ".join(
                missing_features
            )
        )


    if missing_targets:

        raise ValueError(
            "Missing target columns: "
            + ", ".join(
                missing_targets
            )
        )


    X = df[
        FEATURE_COLUMNS
    ].copy()


    y = df[
        TARGET_COLUMNS
    ].copy()


    return df, X, y