from extensions import db


class PanchayatFeature(db.Model):

    __tablename__ = "panchayat_features"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    panchayat_id = db.Column(
        db.Integer,
        db.ForeignKey("panchayats.id"),
        nullable=False,
        unique=True
    )

    # ---------------------------------------------------------
    # Geographic features
    # ---------------------------------------------------------

    latitude = db.Column(
        db.Float,
        nullable=True
    )

    longitude = db.Column(
        db.Float,
        nullable=True
    )

    elevation_m = db.Column(
        db.Float,
        nullable=True
    )

    # ---------------------------------------------------------
    # Local environmental features
    # ---------------------------------------------------------

    land_cover = db.Column(
        db.String(100),
        nullable=True
    )

    water_proximity_km = db.Column(
        db.Float,
        nullable=True
    )

    terrain_type = db.Column(
        db.String(100),
        nullable=True
    )

    # ---------------------------------------------------------
    # Vulnerability / contextual features
    # ---------------------------------------------------------

    historical_flood_susceptibility = db.Column(
        db.Float,
        nullable=True
    )

    vegetation_index = db.Column(
        db.Float,
        nullable=True
    )

    source = db.Column(
        db.String(80),
        nullable=False,
        default="DEMO"
    )

    data_type = db.Column(
        db.String(30),
        nullable=False,
        default="SIMULATED"
    )

    panchayat = db.relationship(
        "Panchayat",
        backref=db.backref(
            "features",
            uselist=False
        )
    )