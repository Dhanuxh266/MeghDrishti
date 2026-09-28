from datetime import datetime

from extensions import db


class PanchayatPrediction(db.Model):
    __tablename__ = "panchayat_predictions"

    id = db.Column(db.Integer, primary_key=True)

    panchayat_id = db.Column(
        db.Integer,
        db.ForeignKey("panchayats.id"),
        nullable=False,
        index=True
    )

    prediction_time = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow,
        index=True
    )

    target_time = db.Column(
        db.DateTime,
        nullable=False,
        index=True
    )

    temperature_c = db.Column(db.Float)
    rainfall_mm = db.Column(db.Float)
    humidity_percent = db.Column(db.Float)
    wind_speed_kmh = db.Column(db.Float)

    model_name = db.Column(db.String(100), nullable=False)
    model_version = db.Column(db.String(50), default="meghdrishti-rf-2026-demo")

    source = db.Column(
        db.String(100),
        default="MEGHDRISHTI_AI_DOWNSCALING"
    )

    data_type = db.Column(
        db.String(50),
        default="MODELLED_PREDICTION"
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    panchayat = db.relationship(
        "Panchayat",
        backref=db.backref("predictions", lazy=True)
    )

    def to_dict(self):
        return {
            "id": self.id,
            "panchayat_id": self.panchayat_id,
            "prediction_time": self.prediction_time.isoformat()
            if self.prediction_time else None,
            "target_time": self.target_time.isoformat()
            if self.target_time else None,
            "temperature_c": self.temperature_c,
            "rainfall_mm": self.rainfall_mm,
            "humidity_percent": self.humidity_percent,
            "wind_speed_kmh": self.wind_speed_kmh,
            "model_name": self.model_name,
            "model_version": self.model_version,
            "source": self.source,
            "data_type": self.data_type,
            "created_at": self.created_at.isoformat()
            if self.created_at else None
        }