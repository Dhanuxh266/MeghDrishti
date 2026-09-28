from datetime import datetime

from extensions import db


class Alert(db.Model):
    __tablename__ = "alerts"

    id = db.Column(db.Integer, primary_key=True)
    panchayat_id = db.Column(db.Integer, db.ForeignKey("panchayats.id"), nullable=False, index=True)
    prediction_id = db.Column(db.Integer, db.ForeignKey("panchayat_predictions.id"), nullable=True, index=True)
    severity = db.Column(db.String(20), nullable=False, index=True)
    alert_type = db.Column(db.String(60), nullable=False, default="WEATHER_RISK")
    title = db.Column(db.String(200), nullable=False)
    message = db.Column(db.Text, nullable=False)
    risk_score = db.Column(db.Float, nullable=True)
    status = db.Column(db.String(30), nullable=False, default="ACTIVE", index=True)
    generated_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)
    expires_at = db.Column(db.DateTime, nullable=True)
    resolved_at = db.Column(db.DateTime, nullable=True)

    panchayat = db.relationship("Panchayat", backref=db.backref("alerts", lazy=True))
    prediction = db.relationship("PanchayatPrediction", backref=db.backref("alerts", lazy=True))
    recipients = db.relationship("AlertRecipient", backref="alert", lazy=True, cascade="all, delete-orphan")
    responses = db.relationship("PanchayatResponse", backref="alert", lazy=True, cascade="all, delete-orphan")

    def to_dict(self):
        return {
            "id": self.id,
            "panchayat_id": self.panchayat_id,
            "prediction_id": self.prediction_id,
            "severity": self.severity,
            "alert_type": self.alert_type,
            "title": self.title,
            "message": self.message,
            "risk_score": self.risk_score,
            "status": self.status,
            "generated_at": self.generated_at.isoformat() if self.generated_at else None,
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
            "resolved_at": self.resolved_at.isoformat() if self.resolved_at else None,
            "panchayat": {
                "id": self.panchayat.id,
                "name": self.panchayat.name,
            } if self.panchayat else None,
        }


class AlertRecipient(db.Model):
    __tablename__ = "alert_recipients"

    id = db.Column(db.Integer, primary_key=True)
    alert_id = db.Column(db.Integer, db.ForeignKey("alerts.id"), nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    channel = db.Column(db.String(30), nullable=False, default="IN_APP")
    delivery_status = db.Column(db.String(30), nullable=False, default="QUEUED")
    delivered_at = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    user = db.relationship("User", backref=db.backref("alert_recipients", lazy=True))

    def to_dict(self):
        return {
            "id": self.id,
            "alert_id": self.alert_id,
            "user_id": self.user_id,
            "channel": self.channel,
            "delivery_status": self.delivery_status,
            "delivered_at": self.delivered_at.isoformat() if self.delivered_at else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class PanchayatResponse(db.Model):
    __tablename__ = "panchayat_responses"

    id = db.Column(db.Integer, primary_key=True)
    alert_id = db.Column(db.Integer, db.ForeignKey("alerts.id"), nullable=False, index=True)
    panchayat_id = db.Column(db.Integer, db.ForeignKey("panchayats.id"), nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    status = db.Column(db.String(30), nullable=False, default="ACKNOWLEDGED")
    note = db.Column(db.Text, nullable=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    panchayat = db.relationship("Panchayat", backref=db.backref("responses", lazy=True))
    user = db.relationship("User", backref=db.backref("panchayat_responses", lazy=True))

    def to_dict(self):
        return {
            "id": self.id,
            "alert_id": self.alert_id,
            "panchayat_id": self.panchayat_id,
            "user_id": self.user_id,
            "status": self.status,
            "note": self.note,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "user_name": self.user.name if self.user else None,
        }
