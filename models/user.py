from datetime import datetime

from extensions import db


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    name = db.Column(
        db.String(120),
        nullable=False
    )

    email = db.Column(
        db.String(160),
        unique=True,
        nullable=True
    )

    mobile = db.Column(
        db.String(20),
        unique=True,
        nullable=True
    )

    password_hash = db.Column(
        db.String(255),
        nullable=False
    )

    role = db.Column(
        db.String(40),
        nullable=False,
        default="citizen"
    )

    is_active = db.Column(
        db.Boolean,
        default=True,
        nullable=False
    )

    state_id = db.Column(
        db.Integer,
        db.ForeignKey("states.id"),
        nullable=True
    )

    district_id = db.Column(
        db.Integer,
        db.ForeignKey("districts.id"),
        nullable=True
    )

    taluka_id = db.Column(
        db.Integer,
        db.ForeignKey("talukas.id"),
        nullable=True
    )

    panchayat_id = db.Column(
        db.Integer,
        db.ForeignKey("panchayats.id"),
        nullable=True
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    state = db.relationship(
        "State",
        foreign_keys=[state_id]
    )

    district = db.relationship(
        "District",
        foreign_keys=[district_id]
    )

    taluka = db.relationship(
        "Taluka",
        foreign_keys=[taluka_id]
    )

    panchayat = db.relationship(
        "Panchayat",
        foreign_keys=[panchayat_id]
    )