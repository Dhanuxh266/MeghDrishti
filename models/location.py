from extensions import db


class State(db.Model):
    __tablename__ = "states"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), unique=True, nullable=False)

    districts = db.relationship(
        "District",
        backref="state",
        lazy=True,
        cascade="all, delete-orphan"
    )


class District(db.Model):
    __tablename__ = "districts"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)

    state_id = db.Column(
        db.Integer,
        db.ForeignKey("states.id"),
        nullable=False
    )

    talukas = db.relationship(
        "Taluka",
        backref="district",
        lazy=True,
        cascade="all, delete-orphan"
    )

    __table_args__ = (
        db.UniqueConstraint(
            "state_id",
            "name",
            name="uq_district_state_name"
        ),
    )


class Taluka(db.Model):
    __tablename__ = "talukas"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)

    district_id = db.Column(
        db.Integer,
        db.ForeignKey("districts.id"),
        nullable=False
    )

    panchayats = db.relationship(
        "Panchayat",
        backref="taluka",
        lazy=True,
        cascade="all, delete-orphan"
    )

    __table_args__ = (
        db.UniqueConstraint(
            "district_id",
            "name",
            name="uq_taluka_district_name"
        ),
    )


class Panchayat(db.Model):
    __tablename__ = "panchayats"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(160), nullable=False)

    taluka_id = db.Column(
        db.Integer,
        db.ForeignKey("talukas.id"),
        nullable=False
    )

    latitude = db.Column(db.Float, nullable=True)
    longitude = db.Column(db.Float, nullable=True)

    elevation_m = db.Column(db.Float, nullable=True)

    population = db.Column(db.Integer, nullable=True)

    area_sq_km = db.Column(db.Float, nullable=True)

    __table_args__ = (
        db.UniqueConstraint(
            "taluka_id",
            "name",
            name="uq_panchayat_taluka_name"
        ),
    )