from datetime import datetime

from extensions import db


class WeatherObservation(db.Model):
    __tablename__ = "weather_observations"

    id = db.Column(db.Integer, primary_key=True)

    panchayat_id = db.Column(
        db.Integer,
        db.ForeignKey("panchayats.id"),
        nullable=False
    )

    observed_at = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow
    )

    temperature_c = db.Column(db.Float)
    feels_like_c = db.Column(db.Float)
    humidity_percent = db.Column(db.Float)

    rainfall_mm = db.Column(db.Float)
    precipitation_mm = db.Column(db.Float)

    wind_speed_kmh = db.Column(db.Float)
    pressure_hpa = db.Column(db.Float)

    weather_code = db.Column(db.Integer)

    source = db.Column(
        db.String(80),
        nullable=False,
        default="Open-Meteo"
    )

    data_type = db.Column(
        db.String(30),
        nullable=False,
        default="LIVE"
    )

    panchayat = db.relationship(
        "Panchayat",
        backref=db.backref(
            "weather_observations",
            lazy=True
        )
    )


class WeatherForecast(db.Model):
    __tablename__ = "weather_forecasts"

    id = db.Column(db.Integer, primary_key=True)

    panchayat_id = db.Column(
        db.Integer,
        db.ForeignKey("panchayats.id"),
        nullable=False
    )

    forecast_time = db.Column(
        db.DateTime,
        nullable=False
    )

    temperature_c = db.Column(db.Float)

    apparent_temperature_c = db.Column(db.Float)

    humidity_percent = db.Column(db.Float)

    precipitation_probability = db.Column(db.Float)

    precipitation_mm = db.Column(db.Float)

    rain_mm = db.Column(db.Float)

    wind_speed_kmh = db.Column(db.Float)

    pressure_hpa = db.Column(db.Float)

    weather_code = db.Column(db.Integer)

    source = db.Column(
        db.String(80),
        nullable=False,
        default="Open-Meteo"
    )

    data_type = db.Column(
        db.String(30),
        nullable=False,
        default="LIVE"
    )

    panchayat = db.relationship(
        "Panchayat",
        backref=db.backref(
            "weather_forecasts",
            lazy=True
        )
    )