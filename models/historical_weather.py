from datetime import datetime

from extensions import db


class HistoricalWeather(db.Model):

    __tablename__ = "historical_weather"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    panchayat_id = db.Column(
        db.Integer,
        db.ForeignKey("panchayats.id"),
        nullable=False
    )

    observation_date = db.Column(
        db.Date,
        nullable=False
    )

    temperature_c = db.Column(
        db.Float,
        nullable=True
    )

    rainfall_mm = db.Column(
        db.Float,
        nullable=True
    )

    humidity_percent = db.Column(
        db.Float,
        nullable=True
    )

    wind_speed_kmh = db.Column(
        db.Float,
        nullable=True
    )

    pressure_hpa = db.Column(
        db.Float,
        nullable=True
    )

    source = db.Column(
        db.String(100),
        nullable=False,
        default="DEMO_DATASET"
    )

    data_type = db.Column(
        db.String(30),
        nullable=False,
        default="SIMULATED"
    )

    created_at = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow
    )

    panchayat = db.relationship(
        "Panchayat",
        backref=db.backref(
            "historical_weather",
            lazy=True
        )
    )