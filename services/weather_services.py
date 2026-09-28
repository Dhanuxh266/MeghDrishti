from datetime import datetime

import requests


OPEN_METEO_URL = "https://api.open-meteo.com/v1/forecast"


def fetch_weather(
    latitude,
    longitude,
    elevation=None,
    forecast_days=7
):
    """
    Fetch current + hourly + daily weather
    for a Panchayat location.

    Source:
    Open-Meteo Forecast API
    """

    params = {
        "latitude": latitude,
        "longitude": longitude,

        "current": ",".join([
            "temperature_2m",
            "relative_humidity_2m",
            "apparent_temperature",
            "precipitation",
            "rain",
            "weather_code",
            "wind_speed_10m",
            "surface_pressure"
        ]),

        "hourly": ",".join([
            "temperature_2m",
            "relative_humidity_2m",
            "apparent_temperature",
            "precipitation_probability",
            "precipitation",
            "rain",
            "weather_code",
            "wind_speed_10m",
            "surface_pressure"
        ]),

        "daily": ",".join([
            "temperature_2m_max",
            "temperature_2m_min",
            "apparent_temperature_max",
            "apparent_temperature_min",
            "precipitation_sum",
            "rain_sum",
            "precipitation_probability_max",
            "weather_code",
            "wind_speed_10m_max"
        ]),

        "timezone": "Asia/Kolkata",

        "forecast_days": forecast_days
    }

    if elevation is not None:
        params["elevation"] = elevation

    response = requests.get(
        OPEN_METEO_URL,
        params=params,
        timeout=20
    )

    response.raise_for_status()

    return response.json()


def parse_current_weather(data):
    current = data.get("current", {})

    return {
        "observed_at": parse_datetime(
            current.get("time")
        ),

        "temperature_c": current.get(
            "temperature_2m"
        ),

        "feels_like_c": current.get(
            "apparent_temperature"
        ),

        "humidity_percent": current.get(
            "relative_humidity_2m"
        ),

        "precipitation_mm": current.get(
            "precipitation"
        ),

        "rainfall_mm": current.get(
            "rain"
        ),

        "wind_speed_kmh": current.get(
            "wind_speed_10m"
        ),

        "pressure_hpa": current.get(
            "surface_pressure"
        ),

        "weather_code": current.get(
            "weather_code"
        )
    }


def parse_hourly_forecast(data):
    hourly = data.get("hourly", {})

    times = hourly.get("time", [])

    result = []

    for i, time_value in enumerate(times):

        result.append({
            "forecast_time": parse_datetime(
                time_value
            ),

            "temperature_c": get_value(
                hourly,
                "temperature_2m",
                i
            ),

            "apparent_temperature_c": get_value(
                hourly,
                "apparent_temperature",
                i
            ),

            "humidity_percent": get_value(
                hourly,
                "relative_humidity_2m",
                i
            ),

            "precipitation_probability": get_value(
                hourly,
                "precipitation_probability",
                i
            ),

            "precipitation_mm": get_value(
                hourly,
                "precipitation",
                i
            ),

            "rain_mm": get_value(
                hourly,
                "rain",
                i
            ),

            "wind_speed_kmh": get_value(
                hourly,
                "wind_speed_10m",
                i
            ),

            "pressure_hpa": get_value(
                hourly,
                "surface_pressure",
                i
            ),

            "weather_code": get_value(
                hourly,
                "weather_code",
                i
            )
        })

    return result


def get_value(data, key, index):

    values = data.get(key, [])

    if index >= len(values):
        return None

    return values[index]


def parse_datetime(value):

    if not value:
        return datetime.utcnow()

    return datetime.fromisoformat(
        value.replace("Z", "+00:00")
    )