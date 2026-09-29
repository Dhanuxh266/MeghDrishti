import json
import os
from datetime import datetime, timedelta

import joblib
import pandas as pd

from models.location import Panchayat
from models.panchayat_features import PanchayatFeature
from models.historical_weather import HistoricalWeather
from models.weather import WeatherObservation, WeatherForecast


# ============================================================
# PATH CONFIGURATION
# ============================================================

BASE_DIR = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)

MODEL_DIR = os.path.join(
    BASE_DIR,
    "ml",
    "models"
)

SELECTED_MODEL_PATH = os.path.join(
    MODEL_DIR,
    "random_forest.joblib"
)

METRICS_PATH = os.path.join(
    MODEL_DIR,
    "model_metrics.json"
)


# ============================================================
# MODEL CACHE
# ============================================================

_MODEL = None
_METRICS = None


# ============================================================
# LOAD TRAINED MODEL
# ============================================================

def load_model():
    """
    Load the selected trained AI model.

    The model is loaded only once and then cached.
    """

    global _MODEL

    if _MODEL is not None:
        return _MODEL

    if not os.path.exists(SELECTED_MODEL_PATH):
        raise FileNotFoundError(
            "Selected Random Forest AI model not found: "
            f"{SELECTED_MODEL_PATH}"
        )

    _MODEL = joblib.load(
        SELECTED_MODEL_PATH
    )

    return _MODEL


# ============================================================
# LOAD MODEL METRICS
# ============================================================

def load_metrics():
    """
    Load model evaluation metrics if available.
    """

    global _METRICS

    if _METRICS is not None:
        return _METRICS

    if not os.path.exists(METRICS_PATH):
        _METRICS = {}
        return _METRICS

    try:

        with open(
            METRICS_PATH,
            "r",
            encoding="utf-8"
        ) as file:

            _METRICS = json.load(file)

    except Exception:

        _METRICS = {}

    return _METRICS


# ============================================================
# MODEL INFORMATION
# ============================================================

def get_model_info():

    metrics = load_metrics()

    model_name = "MEGHDRISHTI_SELECTED_MODEL"

    if isinstance(metrics, dict):

        selected_model = metrics.get(
            "selected_model"
        )

        if selected_model:
            model_name = str(
                selected_model
            )

        elif metrics.get("best_model"):
            model_name = str(
                metrics["best_model"]
            )

    return {
        "model_name": model_name,
        "model_version": str(metrics.get("model_version", "meghdrishti-rf-2026-demo")),
        "evaluation_available": bool(
            metrics
        )
    }


# ============================================================
# SAFE FLOAT CONVERSION
# ============================================================

def safe_float(value, default=0.0):

    try:

        if value is None:
            return default

        return float(value)

    except (
        TypeError,
        ValueError
    ):

        return default


# ============================================================
# LATEST HISTORICAL WEATHER
# ============================================================

def get_latest_historical_weather(
    panchayat_id
):

    return (
        HistoricalWeather.query
        .filter_by(
            panchayat_id=panchayat_id
        )
        .order_by(
            HistoricalWeather.observation_date.desc()
        )
        .first()
    )


# ============================================================
# PREVIOUS HISTORICAL WEATHER
# ============================================================

def get_previous_historical_weather(
    panchayat_id,
    latest_record
):

    if latest_record is None:
        return None

    return (
        HistoricalWeather.query
        .filter(
            HistoricalWeather.panchayat_id
            == panchayat_id,

            HistoricalWeather.observation_date
            < latest_record.observation_date
        )
        .order_by(
            HistoricalWeather.observation_date.desc()
        )
        .first()
    )


# ============================================================
# LATEST LIVE WEATHER
# ============================================================

def get_latest_live_weather(
    panchayat_id
):

    return (
        WeatherObservation.query
        .filter_by(
            panchayat_id=panchayat_id
        )
        .order_by(
            WeatherObservation.observed_at.desc()
        )
        .first()
    )


# ============================================================
# LATEST FORECAST
# ============================================================

def get_latest_forecast(
    panchayat_id
):

    now = datetime.utcnow()

    forecast = (
        WeatherForecast.query
        .filter(
            WeatherForecast.panchayat_id
            == panchayat_id,

            WeatherForecast.forecast_time
            >= now
        )
        .order_by(
            WeatherForecast.forecast_time.asc()
        )
        .first()
    )

    if forecast is not None:
        return forecast

    return (
        WeatherForecast.query
        .filter_by(
            panchayat_id=panchayat_id
        )
        .order_by(
            WeatherForecast.forecast_time.desc()
        )
        .first()
    )


# ============================================================
# COARSE WEATHER
# ============================================================

def get_coarse_weather(
    panchayat_id
):

    forecast = get_latest_forecast(
        panchayat_id
    )

    # --------------------------------------------------------
    # LIVE FORECAST
    # --------------------------------------------------------

    if forecast is not None:

        return {

            "temperature_c":
                safe_float(
                    forecast.temperature_c
                ),

            "rainfall_mm":
                safe_float(
                    getattr(
                        forecast,
                        "rain_mm",
                        getattr(
                            forecast,
                            "precipitation_mm",
                            0.0
                        )
                    )
                ),

            "humidity_percent":
                safe_float(
                    forecast.humidity_percent
                ),

            "wind_speed_kmh":
                safe_float(
                    forecast.wind_speed_kmh
                ),

            "pressure_hpa":
                safe_float(
                    forecast.pressure_hpa
                ),

            "source":
                getattr(
                    forecast,
                    "source",
                    "WEATHER_FORECAST"
                ),

            "target_time":
                forecast.forecast_time
        }

    # --------------------------------------------------------
    # LIVE OBSERVATION FALLBACK
    # --------------------------------------------------------

    observation = get_latest_live_weather(
        panchayat_id
    )

    if observation is not None:

        return {

            "temperature_c":
                safe_float(
                    observation.temperature_c
                ),

            "rainfall_mm":
                safe_float(
                    observation.rainfall_mm
                ),

            "humidity_percent":
                safe_float(
                    observation.humidity_percent
                ),

            "wind_speed_kmh":
                safe_float(
                    observation.wind_speed_kmh
                ),

            "pressure_hpa":
                safe_float(
                    observation.pressure_hpa
                ),

            "source":
                getattr(
                    observation,
                    "source",
                    "WEATHER_OBSERVATION"
                ),

            "target_time":
                observation.observed_at
                + timedelta(days=1)
        }

    # --------------------------------------------------------
    # HISTORICAL / DEMO DATA FALLBACK
    # --------------------------------------------------------

    historical = (
        get_latest_historical_weather(
            panchayat_id
        )
    )

    if historical is not None:

        return {

            "temperature_c":
                safe_float(
                    historical.temperature_c
                ),

            "rainfall_mm":
                safe_float(
                    historical.rainfall_mm
                ),

            "humidity_percent":
                safe_float(
                    historical.humidity_percent
                ),

            "wind_speed_kmh":
                safe_float(
                    historical.wind_speed_kmh
                ),

            "pressure_hpa":
                safe_float(
                    historical.pressure_hpa
                ),

            "source":
                getattr(
                    historical,
                    "source",
                    "DEMO_DATASET"
                ),

            "target_time":
                datetime.combine(
                    historical.observation_date,
                    datetime.min.time()
                )
                + timedelta(days=1)
        }

    raise ValueError(
        "No weather data is available "
        f"for Panchayat {panchayat_id}."
    )

# ============================================================
# BUILD MODEL FEATURES
# ============================================================

def build_prediction_features(
    panchayat_id
):
    panchayat = Panchayat.query.get(
        panchayat_id
    )

    if panchayat is None:

        raise ValueError(
            f"Panchayat {panchayat_id} "
            "does not exist."
        )

    panchayat_features = (
        PanchayatFeature.query
        .filter_by(
            panchayat_id=panchayat_id
        )
        .first()
    )

    if panchayat_features is None:

        raise ValueError(
            "Panchayat geographical features "
            f"are missing for Panchayat {panchayat_id}."
        )

    latest_history = (
        get_latest_historical_weather(
            panchayat_id
        )
    )

    previous_history = (
        get_previous_historical_weather(
            panchayat_id,
            latest_history
        )
    )

    coarse = get_coarse_weather(
        panchayat_id
    )

    target_time = coarse[
        "target_time"
    ]

    if target_time is None:

        target_time = (
            datetime.utcnow()
            + timedelta(days=1)
        )

    # --------------------------------------------------------
    # Historical weather
    # --------------------------------------------------------

    if latest_history is not None:

        historical_temperature = safe_float(
            latest_history.temperature_c
        )

        historical_rainfall = safe_float(
            latest_history.rainfall_mm
        )

        historical_humidity = safe_float(
            latest_history.humidity_percent
        )

        historical_wind = safe_float(
            latest_history.wind_speed_kmh
        )

        historical_pressure = safe_float(
            latest_history.pressure_hpa
        )

    else:

        historical_temperature = coarse[
            "temperature_c"
        ]

        historical_rainfall = coarse[
            "rainfall_mm"
        ]

        historical_humidity = coarse[
            "humidity_percent"
        ]

        historical_wind = coarse[
            "wind_speed_kmh"
        ]

        historical_pressure = coarse[
            "pressure_hpa"
        ]

    # --------------------------------------------------------
    # Previous day / lag weather
    # --------------------------------------------------------

    if previous_history is not None:

        previous_temperature = safe_float(
            previous_history.temperature_c
        )

        previous_rainfall = safe_float(
            previous_history.rainfall_mm
        )

        previous_humidity = safe_float(
            previous_history.humidity_percent
        )

    else:

        previous_temperature = (
            historical_temperature
        )

        previous_rainfall = (
            historical_rainfall
        )

        previous_humidity = (
            historical_humidity
        )

    # --------------------------------------------------------
    # Geographic values
    # --------------------------------------------------------

    latitude = safe_float(
        getattr(
            panchayat_features,
            "latitude",
            getattr(
                panchayat,
                "latitude",
                0
            )
        )
    )

    longitude = safe_float(
        getattr(
            panchayat_features,
            "longitude",
            getattr(
                panchayat,
                "longitude",
                0
            )
        )
    )

    elevation = safe_float(
        getattr(
            panchayat_features,
            "elevation_m",
            getattr(
                panchayat,
                "elevation_m",
                0
            )
        )
    )

    water_proximity = safe_float(
        getattr(
            panchayat_features,
            "water_proximity_km",
            0
        )
    )

    flood_susceptibility = safe_float(
        getattr(
            panchayat_features,
            "historical_flood_susceptibility",
            0
        )
    )

    vegetation_index = safe_float(
        getattr(
            panchayat_features,
            "vegetation_index",
            0
        )
    )

    land_cover = getattr(
        panchayat_features,
        "land_cover",
        "UNKNOWN"
    )

    terrain_type = getattr(
        panchayat_features,
        "terrain_type",
        "UNKNOWN"
    )

    # --------------------------------------------------------
    # Final model row
    # --------------------------------------------------------

    row = {

        "coarse_temperature_c":
            coarse["temperature_c"],

        "coarse_rainfall_mm":
            coarse["rainfall_mm"],

        "coarse_humidity_percent":
            coarse["humidity_percent"],

        "coarse_wind_speed_kmh":
            coarse["wind_speed_kmh"],

        "coarse_pressure_hpa":
            coarse["pressure_hpa"],

        "latitude":
            latitude,

        "longitude":
            longitude,

        "elevation_m":
            elevation,

        "water_proximity_km":
            water_proximity,

        "historical_flood_susceptibility":
            flood_susceptibility,

        "vegetation_index":
            vegetation_index,

        "land_cover":
            land_cover,

        "terrain_type":
            terrain_type,

        "historical_temperature_c":
            historical_temperature,

        "historical_rainfall_mm":
            historical_rainfall,

        "historical_humidity_percent":
            historical_humidity,

        "historical_wind_speed_kmh":
            historical_wind,

        "historical_pressure_hpa":
            historical_pressure,

        "previous_temperature_c":
            previous_temperature,

        "previous_rainfall_mm":
            previous_rainfall,

        "previous_humidity_percent":
            previous_humidity,

        "month":
            target_time.month,

        "day_of_year":
            target_time.timetuple().tm_yday
    }

    return (
        pd.DataFrame([row]),
        target_time,
        coarse
    )


# ============================================================
# PANCHAYAT WEATHER PREDICTION
# ============================================================

def predict_panchayat_weather(
    panchayat_id
):
    """
    Generate Panchayat-level weather prediction.

    Output:

        temperature
        rainfall
        humidity
        wind
        model information
        prediction metadata
    """

    model = load_model()

    (
        X,
        target_time,
        coarse
    ) = build_prediction_features(
        panchayat_id
    )

    # --------------------------------------------------------
    # Run trained model
    # --------------------------------------------------------

    prediction = model.predict(
        X
    )

    prediction = prediction[0]

    if len(prediction) < 4:

        raise ValueError(
            "The trained model returned "
            "fewer than four weather outputs."
        )

    temperature = safe_float(
        prediction[0]
    )

    rainfall = max(
        0.0,
        safe_float(
            prediction[1]
        )
    )

    humidity = min(
        100.0,
        max(
            0.0,
            safe_float(
                prediction[2]
            )
        )
    )

    wind = max(
        0.0,
        safe_float(
            prediction[3]
        )
    )

    model_info = get_model_info()

    return {

        "panchayat_id":
            panchayat_id,

        "target_time":
            target_time,

        "temperature_c":
            round(
                temperature,
                2
            ),

        "rainfall_mm":
            round(
                rainfall,
                2
            ),

        "humidity_percent":
            round(
                humidity,
                2
            ),

        "wind_speed_kmh":
            round(
                wind,
                2
            ),

        "model_name":
            model_info[
                "model_name"
            ],

        "model_version":
            model_info[
                "model_version"
            ],

        "source":
            "MEGHDRISHTI_AI_DOWNSCALING",

        "data_type":
            "MODELLED_PREDICTION",

        "coarse_weather_source":
            coarse[
                "source"
            ],

        "prediction_generated_at":
            datetime.utcnow()
    }