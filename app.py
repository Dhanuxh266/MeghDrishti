import os
import re
from datetime import datetime
from models.prediction import PanchayatPrediction
from models.alert import Alert, AlertRecipient, PanchayatResponse
from services.ai_service import predict_panchayat_weather
from services.risk_service import calculate_risk
from services.notification_service import build_sms_message, normalize_indian_mobile, provider_status, send_sms
import requests
from dotenv import load_dotenv
from flask import (
    Flask,
    jsonify,
    render_template,
    request,
    redirect,
    url_for,
    session,
    flash,
    abort,
)
from werkzeug.security import check_password_hash, generate_password_hash

from extensions import db

load_dotenv()


# ============================================================
# APPLICATION FACTORY
# ============================================================

def create_app():

    app = Flask(
        __name__,
        template_folder="frontend/templates",
        static_folder="frontend/static",
    )

    # ========================================================
    # CONFIGURATION
    # ========================================================

    app.config["SECRET_KEY"] = os.getenv(
        "SECRET_KEY",
        "dev-only-change-me",
    )

    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv(
        "DATABASE_URL",
        "sqlite:///meghdrishti.db",
    )

    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    # Initialize database
    db.init_app(app)

    # ========================================================
    # MODELS
    # ========================================================

    from models.user import User

    from models.location import (
        State,
        District,
        Taluka,
        Panchayat,
    )

    # Weather Models
    from models.weather import (
        WeatherObservation,
        WeatherForecast,
    )
    from models.panchayat_features import PanchayatFeature

    from models.historical_weather import HistoricalWeather

    # ========================================================
    # WEATHER SERVICE
    #
    # IMPORTANT:
    # Your project uses weather_services.py
    # ========================================================

    from services.weather_services import (
        fetch_weather,
        parse_current_weather,
        parse_hourly_forecast,
    )

    # ========================================================
    # ROLE CONFIGURATION
    # ========================================================

    ROLE_TITLES = {
        "government": "Government Dashboard",
        "panchayat_official": "Panchayat Official Dashboard",
        "citizen": "Citizen Dashboard",
    }

    VALID_ROLES = set(ROLE_TITLES.keys())

    # ========================================================
    # LOGIN
    # ========================================================

    @app.get("/")
    def index():

        if session.get("user_id"):
            return redirect(url_for("dashboard"))

        return render_template("login.html")

    # ========================================================
    # LOGIN POST
    # ========================================================

    # ========================================================
    # NEW CITIZEN REGISTRATION
    # ========================================================

    @app.route("/register", methods=["GET", "POST"])
    def register():

        if session.get("user_id"):
            return redirect(url_for("dashboard"))

        if request.method == "GET":
            return render_template("register.html")

        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower() or None
        mobile = request.form.get("mobile", "").strip()
        password = request.form.get("password", "")
        confirm_password = request.form.get("confirm_password", "")
        panchayat_id = request.form.get("panchayat_id", "").strip()

        if not name or not mobile or not password or not confirm_password or not panchayat_id:
            flash("Complete all required fields and select a Panchayat.", "error")
            return redirect(url_for("register"))

        if len(name) < 2:
            flash("Enter a valid name.", "error")
            return redirect(url_for("register"))

        if not re.fullmatch(r"[6-9]\d{9}", mobile):
            flash("Enter a valid 10-digit Indian mobile number.", "error")
            return redirect(url_for("register"))

        if email and not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", email):
            flash("Enter a valid email address.", "error")
            return redirect(url_for("register"))

        if len(password) < 8:
            flash("Password must contain at least 8 characters.", "error")
            return redirect(url_for("register"))

        if password != confirm_password:
            flash("Passwords do not match.", "error")
            return redirect(url_for("register"))

        try:
            panchayat_id_int = int(panchayat_id)
        except ValueError:
            flash("Select a valid Panchayat.", "error")
            return redirect(url_for("register"))

        panchayat = db.session.get(Panchayat, panchayat_id_int)
        if not panchayat:
            flash("Selected Panchayat was not found.", "error")
            return redirect(url_for("register"))

        taluka = panchayat.taluka
        district = taluka.district if taluka else None
        state = district.state if district else None

        if User.query.filter_by(mobile=mobile).first():
            flash("An account with this mobile number already exists.", "error")
            return redirect(url_for("register"))

        if email and User.query.filter_by(email=email).first():
            flash("An account with this email already exists.", "error")
            return redirect(url_for("register"))

        user = User(
            name=name,
            email=email,
            mobile=mobile,
            password_hash=generate_password_hash(password),
            role="citizen",
            is_active=True,
            state_id=state.id if state else None,
            district_id=district.id if district else None,
            taluka_id=taluka.id if taluka else None,
            panchayat_id=panchayat.id,
        )

        db.session.add(user)
        db.session.commit()

        flash("Account created successfully. You can now log in.", "success")
        return redirect(url_for("index"))

    @app.post("/login")
    def login():

        identifier = request.form.get(
            "identifier",
            "",
        ).strip()

        password = request.form.get(
            "password",
            "",
        )

        if not identifier or not password:

            flash(
                "Enter your email/mobile and password.",
                "error",
            )

            return redirect(url_for("index"))

        # Search by email OR mobile
        user = User.query.filter(
            (User.email == identifier)
            | (User.mobile == identifier)
        ).first()

        if not user:

            flash(
                "Invalid credentials.",
                "error",
            )

            return redirect(url_for("index"))

        # Password verification
        if not check_password_hash(
            user.password_hash,
            password,
        ):

            flash(
                "Invalid credentials.",
                "error",
            )

            return redirect(url_for("index"))

        # Account status
        if not user.is_active:

            flash(
                "This account is inactive.",
                "error",
            )

            return redirect(url_for("index"))

        # Role validation
        if user.role not in VALID_ROLES:

            flash(
                "Invalid account role.",
                "error",
            )

            return redirect(url_for("index"))

        # Clear previous session
        session.clear()

        # Create authenticated session
        session["user_id"] = user.id
        session["role"] = user.role

        return redirect(
            url_for("dashboard")
        )

    # ========================================================
    # AUTHENTICATION HELPERS
    # ========================================================

    def require_login():

        if not session.get("user_id"):

            return redirect(
                url_for("index")
            )

        return None

    def require_role(*allowed_roles):

        if not session.get("user_id"):

            return redirect(
                url_for("index")
            )

        if session.get("role") not in allowed_roles:

            abort(403)

        return None

    def get_current_user():

        user_id = session.get("user_id")

        if not user_id:
            return None

        return db.session.get(
            User,
            user_id,
        )

    # ========================================================
    # PANCHAYAT ACCESS HELPER
    #
    # Government:
    #     Can access all Panchayats.
    #
    # Panchayat Official:
    #     Only assigned Panchayat.
    #
    # Citizen:
    #     Currently allowed to view Panchayat weather.
    #     Their registered Panchayat is the default in UI.
    # ========================================================

    def check_panchayat_access(panchayat):

        user = get_current_user()

        if not user:

            return jsonify({
                "error": "Authentication required"
            }), 401

        # Government has global access
        if user.role == "government":
            return None

        # Panchayat official can only access assigned Panchayat
        if user.role == "panchayat_official":

            if (
                not user.panchayat
                or user.panchayat.id != panchayat.id
            ):

                return jsonify({
                    "error": "Access denied for this Panchayat"
                }), 403

        # Citizen
        # Citizens may view Panchayat information.
        # Their registered Panchayat is handled by the frontend.
        return None

    # ========================================================
    # DASHBOARD
    # ========================================================

    @app.get("/dashboard")
    def dashboard():

        login_check = require_login()

        if login_check:
            return login_check

        user = get_current_user()

        if not user:

            session.clear()

            return redirect(
                url_for("index")
            )

        role = user.role

        # ----------------------------------------------------
        # GOVERNMENT
        # ----------------------------------------------------

        if role == "government":

            return render_template(
                "dashboard.html",
                role=role,
                role_title=ROLE_TITLES[role],
                user=user,
                scope="All Panchayats",
            )

        # ----------------------------------------------------
        # PANCHAYAT OFFICIAL
        # ----------------------------------------------------

        if role == "panchayat_official":

            return render_template(
                "dashboard.html",
                role=role,
                role_title=ROLE_TITLES[role],
                user=user,
                scope=(
                    user.panchayat.name
                    if user.panchayat
                    else "Assigned Panchayat"
                ),
            )

        # ----------------------------------------------------
        # CITIZEN
        # ----------------------------------------------------

        return render_template(
            "dashboard.html",
            role=role,
            role_title=ROLE_TITLES[role],
            user=user,
            scope=(
                user.panchayat.name
                if user.panchayat
                else "Local Area"
            ),
        )

    # ========================================================
    # PUBLIC LOCATION API FOR REGISTRATION
    # ========================================================

    @app.get("/api/public/locations/states")
    def get_public_states():
        return jsonify([
            {"id": state.id, "name": state.name}
            for state in State.query.order_by(State.name).all()
        ])

    @app.get("/api/public/locations/districts/<int:state_id>")
    def get_public_districts(state_id):
        return jsonify([
            {"id": district.id, "name": district.name, "state_id": district.state_id}
            for district in District.query.filter_by(state_id=state_id).order_by(District.name).all()
        ])

    @app.get("/api/public/locations/talukas/<int:district_id>")
    def get_public_talukas(district_id):
        return jsonify([
            {"id": taluka.id, "name": taluka.name, "district_id": taluka.district_id}
            for taluka in Taluka.query.filter_by(district_id=district_id).order_by(Taluka.name).all()
        ])

    @app.get("/api/public/locations/panchayats/<int:taluka_id>")
    def get_public_panchayats(taluka_id):
        return jsonify([
            {"id": panchayat.id, "name": panchayat.name, "taluka_id": panchayat.taluka_id}
            for panchayat in Panchayat.query.filter_by(taluka_id=taluka_id).order_by(Panchayat.name).all()
        ])

    # ========================================================
    # LOCATION API
    # ========================================================

    @app.get("/api/locations/states")
    def get_states():

        if not session.get("user_id"):

            return jsonify({
                "error": "Authentication required"
            }), 401

        states = State.query.order_by(
            State.name
        ).all()

        return jsonify([
            {
                "id": state.id,
                "name": state.name,
            }
            for state in states
        ])

    # ========================================================
    # DISTRICTS
    # ========================================================

    @app.get("/api/locations/districts/<int:state_id>")
    def get_districts(state_id):

        if not session.get("user_id"):

            return jsonify({
                "error": "Authentication required"
            }), 401

        districts = District.query.filter_by(
            state_id=state_id
        ).order_by(
            District.name
        ).all()

        return jsonify([
            {
                "id": district.id,
                "name": district.name,
                "state_id": district.state_id,
            }
            for district in districts
        ])

    # ========================================================
    # TALUKAS
    # ========================================================

    @app.get("/api/locations/talukas/<int:district_id>")
    def get_talukas(district_id):

        if not session.get("user_id"):

            return jsonify({
                "error": "Authentication required"
            }), 401

        talukas = Taluka.query.filter_by(
            district_id=district_id
        ).order_by(
            Taluka.name
        ).all()

        return jsonify([
            {
                "id": taluka.id,
                "name": taluka.name,
                "district_id": taluka.district_id,
            }
            for taluka in talukas
        ])

    # ========================================================
    # PANCHAYATS
    # ========================================================

    @app.get("/api/locations/panchayats/<int:taluka_id>")
    def get_panchayats(taluka_id):

        if not session.get("user_id"):

            return jsonify({
                "error": "Authentication required"
            }), 401

        panchayats = Panchayat.query.filter_by(
            taluka_id=taluka_id
        ).order_by(
            Panchayat.name
        ).all()

        return jsonify([
            {
                "id": panchayat.id,
                "name": panchayat.name,
                "taluka_id": panchayat.taluka_id,
                "latitude": panchayat.latitude,
                "longitude": panchayat.longitude,
                "elevation_m": panchayat.elevation_m,
                "population": panchayat.population,
                "area_sq_km": panchayat.area_sq_km,
            }
            for panchayat in panchayats
        ])

    # ========================================================
    # CURRENT USER API
    # ========================================================

    @app.get("/api/auth/me")
    def current_user():

        if not session.get("user_id"):

            return jsonify({
                "authenticated": False
            })

        user = get_current_user()

        if not user:

            session.clear()

            return jsonify({
                "authenticated": False
            })

        return jsonify({

            "authenticated": True,

            "user": {

                "id": user.id,

                "name": user.name,

                "email": user.email,

                "mobile": user.mobile,

                "role": user.role,

                "state": (
                    user.state.name
                    if user.state
                    else None
                ),

                "district": (
                    user.district.name
                    if user.district
                    else None
                ),

                "taluka": (
                    user.taluka.name
                    if user.taluka
                    else None
                ),

                "panchayat": (
                    user.panchayat.name
                    if user.panchayat
                    else None
                ),

                "panchayat_id": (
                    user.panchayat.id
                    if user.panchayat
                    else None
                ),
            },
        })

# ========================================================
# Weather data
    # PANCHAYAT FEATURES
    # ========================================================

    @app.get(
        "/api/panchayat/<int:panchayat_id>/features"
    )
    def get_panchayat_features(panchayat_id):

        if not session.get("user_id"):

            return jsonify({
                "error": "Authentication required"
            }), 401

        panchayat = db.session.get(
            Panchayat,
            panchayat_id
        )

        if not panchayat:

            return jsonify({
                "error": "Panchayat not found"
            }), 404

        access_error = check_panchayat_access(
            panchayat
        )

        if access_error:
            return access_error

        feature = PanchayatFeature.query.filter_by(
            panchayat_id=panchayat.id
        ).first()

        if not feature:

            return jsonify({
                "error": "Panchayat features not available"
            }), 404

        return jsonify({

            "panchayat": {
                "id": panchayat.id,
                "name": panchayat.name
            },

            "features": {

                "latitude":
                    feature.latitude,

                "longitude":
                    feature.longitude,

                "elevation_m":
                    feature.elevation_m,

                "land_cover":
                    feature.land_cover,

                "water_proximity_km":
                    feature.water_proximity_km,

                "terrain_type":
                    feature.terrain_type,

                "historical_flood_susceptibility":
                    feature.historical_flood_susceptibility,

                "vegetation_index":
                    feature.vegetation_index,

                "source":
                    feature.source,

                "data_type":
                    feature.data_type
            }
        })
    # ========================================================
    # Weather data
    # HISTORICAL WEATHER
    # ========================================================

    @app.get(
        "/api/weather/panchayat/<int:panchayat_id>/historical"
    )
    def get_historical_weather(panchayat_id):

        if not session.get("user_id"):

            return jsonify({
                "error": "Authentication required"
            }), 401

        panchayat = db.session.get(
            Panchayat,
            panchayat_id
        )

        if not panchayat:

            return jsonify({
                "error": "Panchayat not found"
            }), 404

        access_error = check_panchayat_access(
            panchayat
        )

        if access_error:
            return access_error

        records = HistoricalWeather.query.filter_by(
            panchayat_id=panchayat.id
        ).order_by(
            HistoricalWeather.observation_date.desc()
        ).limit(100).all()

        return jsonify({

            "panchayat": panchayat.name,

            "data_type": "SIMULATED",

            "source": "DEMO_DATASET",

            "records": [

                {
                    "date":
                        record.observation_date.isoformat(),

                    "temperature_c":
                        record.temperature_c,

                    "rainfall_mm":
                        record.rainfall_mm,

                    "humidity_percent":
                        record.humidity_percent,

                    "wind_speed_kmh":
                        record.wind_speed_kmh,

                    "pressure_hpa":
                        record.pressure_hpa
                }

                for record in records
            ]
        })
        # ========================================================
        # Weather data
    # WEATHER — CURRENT
    # ========================================================

    @app.get(
        "/api/weather/panchayat/<int:panchayat_id>"
    )
    def panchayat_weather(panchayat_id):

        # ----------------------------------------------------
        # Authentication
        # ----------------------------------------------------

        if not session.get("user_id"):

            return jsonify({
                "error": "Authentication required"
            }), 401

        # ----------------------------------------------------
        # Panchayat lookup
        # ----------------------------------------------------

        panchayat = db.session.get(
            Panchayat,
            panchayat_id,
        )

        if not panchayat:

            return jsonify({
                "error": "Panchayat not found"
            }), 404

        # ----------------------------------------------------
        # Authorization
        # ----------------------------------------------------

        access_error = check_panchayat_access(
            panchayat
        )

        if access_error:
            return access_error

        # ----------------------------------------------------
        # Coordinates
        # ----------------------------------------------------

        if (
            panchayat.latitude is None
            or panchayat.longitude is None
        ):

            return jsonify({
                "error": "Panchayat coordinates unavailable"
            }), 400

        try:

            # ------------------------------------------------
            # Fetch weather
            # ------------------------------------------------

            data = fetch_weather(

                latitude=panchayat.latitude,

                longitude=panchayat.longitude,

                elevation=panchayat.elevation_m,

                forecast_days=7,
            )

            # ------------------------------------------------
            # Parse current weather
            # ------------------------------------------------

            current = parse_current_weather(
                data
            )

            # ------------------------------------------------
            # Store observation
            # ------------------------------------------------

            observation = WeatherObservation(

                panchayat_id=panchayat.id,

                observed_at=current[
                    "observed_at"
                ],

                temperature_c=current[
                    "temperature_c"
                ],

                feels_like_c=current[
                    "feels_like_c"
                ],

                humidity_percent=current[
                    "humidity_percent"
                ],

                rainfall_mm=current[
                    "rainfall_mm"
                ],

                precipitation_mm=current[
                    "precipitation_mm"
                ],

                wind_speed_kmh=current[
                    "wind_speed_kmh"
                ],

                pressure_hpa=current[
                    "pressure_hpa"
                ],

                weather_code=current[
                    "weather_code"
                ],

                source="Open-Meteo",

                data_type="LIVE",
            )

            db.session.add(
                observation
            )

            db.session.commit()

            # ------------------------------------------------
            # Response
            # ------------------------------------------------

            return jsonify({

                "status": "success",

                "source": "Open-Meteo",

                "data_type": "LIVE",

                "panchayat": {

                    "id": panchayat.id,

                    "name": panchayat.name,

                    "latitude": panchayat.latitude,

                    "longitude": panchayat.longitude,

                    "elevation_m": panchayat.elevation_m,
                },

                "weather": current,
            })

        # ----------------------------------------------------
        # Weather API error
        # ----------------------------------------------------

        except requests.RequestException as exc:

            db.session.rollback()

            return jsonify({

                "status": "error",

                "error": "Weather service unavailable",

                "details": str(exc),
            }), 502

        # ----------------------------------------------------
        # Processing/database error
        # ----------------------------------------------------

        except Exception as exc:

            db.session.rollback()

            return jsonify({

                "status": "error",

                "error": "Weather processing failed",

                "details": str(exc),
            }), 500

    # ========================================================
    # WEATHER — FORECAST
    # ========================================================

    @app.get(
        "/api/weather/panchayat/<int:panchayat_id>/forecast"
    )
    def panchayat_forecast(panchayat_id):

        # ----------------------------------------------------
        # Authentication
        # ----------------------------------------------------

        if not session.get("user_id"):

            return jsonify({
                "error": "Authentication required"
            }), 401

        # ----------------------------------------------------
        # Panchayat lookup
        # ----------------------------------------------------

        panchayat = db.session.get(
            Panchayat,
            panchayat_id,
        )

        if not panchayat:

            return jsonify({
                "error": "Panchayat not found"
            }), 404

        # ----------------------------------------------------
        # Authorization
        # ----------------------------------------------------

        access_error = check_panchayat_access(
            panchayat
        )

        if access_error:
            return access_error

        # ----------------------------------------------------
        # Coordinates
        # ----------------------------------------------------

        if (
            panchayat.latitude is None
            or panchayat.longitude is None
        ):

            return jsonify({
                "error": "Panchayat coordinates unavailable"
            }), 400

        try:

            # ------------------------------------------------
            # Fetch weather
            # ------------------------------------------------

            data = fetch_weather(

                latitude=panchayat.latitude,

                longitude=panchayat.longitude,

                elevation=panchayat.elevation_m,

                forecast_days=7,
            )

            # ------------------------------------------------
            # Parse forecast
            # ------------------------------------------------

            forecast = parse_hourly_forecast(
                data
            )

            # ------------------------------------------------
            # Store forecast
            # ------------------------------------------------

            records = []

            for item in forecast:

                record = WeatherForecast(

                    panchayat_id=panchayat.id,

                    forecast_time=item[
                        "forecast_time"
                    ],

                    temperature_c=item[
                        "temperature_c"
                    ],

                    apparent_temperature_c=item[
                        "apparent_temperature_c"
                    ],

                    humidity_percent=item[
                        "humidity_percent"
                    ],

                    precipitation_probability=item[
                        "precipitation_probability"
                    ],

                    precipitation_mm=item[
                        "precipitation_mm"
                    ],

                    rain_mm=item[
                        "rain_mm"
                    ],

                    wind_speed_kmh=item[
                        "wind_speed_kmh"
                    ],

                    pressure_hpa=item[
                        "pressure_hpa"
                    ],

                    weather_code=item[
                        "weather_code"
                    ],

                    source="Open-Meteo",

                    data_type="LIVE",
                )

                db.session.add(record)

                records.append(item)

            db.session.commit()

            # ------------------------------------------------
            # Response
            # ------------------------------------------------

            return jsonify({

                "status": "success",

                "source": "Open-Meteo",

                "data_type": "LIVE",

                "panchayat": {

                    "id": panchayat.id,

                    "name": panchayat.name,

                    "latitude": panchayat.latitude,

                    "longitude": panchayat.longitude,

                    "elevation_m": panchayat.elevation_m,
                },

                "forecast": records,
            })

        # ----------------------------------------------------
        # Weather API error
        # ----------------------------------------------------

        except requests.RequestException as exc:

            db.session.rollback()

            return jsonify({

                "status": "error",

                "error": "Weather service unavailable",

                "details": str(exc),
            }), 502

        # ----------------------------------------------------
        # Processing/database error
        # ----------------------------------------------------

        except Exception as exc:

            db.session.rollback()

            return jsonify({

                "status": "error",

                "error": "Forecast processing failed",

                "details": str(exc),
            }), 500

    # ========================================================
    # WEATHER — LATEST STORED OBSERVATION
    #
    # Useful for dashboard without calling API repeatedly.
    # ========================================================

    @app.get(
        "/api/weather/panchayat/<int:panchayat_id>/latest"
    )
    def latest_weather(panchayat_id):

        if not session.get("user_id"):

            return jsonify({
                "error": "Authentication required"
            }), 401

        panchayat = db.session.get(
            Panchayat,
            panchayat_id,
        )

        if not panchayat:

            return jsonify({
                "error": "Panchayat not found"
            }), 404

        access_error = check_panchayat_access(
            panchayat
        )

        if access_error:
            return access_error

        observation = WeatherObservation.query.filter_by(
            panchayat_id=panchayat.id
        ).order_by(
            WeatherObservation.observed_at.desc()
        ).first()

        if not observation:

            return jsonify({
                "status": "empty",
                "message": "No stored weather observation found."
            }), 404

        return jsonify({

            "status": "success",

            "source": observation.source,

            "data_type": observation.data_type,

            "panchayat": {

                "id": panchayat.id,

                "name": panchayat.name,
            },

            "weather": {

                "observed_at":
                    observation.observed_at,

                "temperature_c":
                    observation.temperature_c,

                "feels_like_c":
                    observation.feels_like_c,

                "humidity_percent":
                    observation.humidity_percent,

                "rainfall_mm":
                    observation.rainfall_mm,

                "precipitation_mm":
                    observation.precipitation_mm,

                "wind_speed_kmh":
                    observation.wind_speed_kmh,

                "pressure_hpa":
                    observation.pressure_hpa,

                "weather_code":
                    observation.weather_code,
            },
        })

    # ========================================================
    # WEATHER — STORED FORECAST
    #
    # Returns the latest stored forecast.
    # ========================================================

    @app.get(
        "/api/weather/panchayat/<int:panchayat_id>/stored-forecast"
    )
    def stored_forecast(panchayat_id):

        if not session.get("user_id"):

            return jsonify({
                "error": "Authentication required"
            }), 401

        panchayat = db.session.get(
            Panchayat,
            panchayat_id,
        )

        if not panchayat:

            return jsonify({
                "error": "Panchayat not found"
            }), 404

        access_error = check_panchayat_access(
            panchayat
        )

        if access_error:
            return access_error

        forecasts = WeatherForecast.query.filter_by(
            panchayat_id=panchayat.id
        ).order_by(
            WeatherForecast.forecast_time.asc()
        ).all()

        return jsonify({

            "status": "success",

            "source": "Open-Meteo",

            "data_type": "LIVE",

            "panchayat": {

                "id": panchayat.id,

                "name": panchayat.name,
            },

            "forecast": [

                {

                    "forecast_time":
                        item.forecast_time,

                    "temperature_c":
                        item.temperature_c,

                    "apparent_temperature_c":
                        item.apparent_temperature_c,

                    "humidity_percent":
                        item.humidity_percent,

                    "precipitation_probability":
                        item.precipitation_probability,

                    "precipitation_mm":
                        item.precipitation_mm,

                    "rain_mm":
                        item.rain_mm,

                    "wind_speed_kmh":
                        item.wind_speed_kmh,

                    "pressure_hpa":
                        item.pressure_hpa,

                    "weather_code":
                        item.weather_code,
                }

                for item in forecasts
            ],
        })
        # ========================================================
    # AI downscaling
    # AI PANCHAYAT-LEVEL PREDICTION
    # ========================================================

    @app.post(
        "/api/ai/panchayat/<int:panchayat_id>/predict"
    )
    def ai_panchayat_prediction(panchayat_id):

        # ----------------------------------------------------
        # Authentication
        # ----------------------------------------------------

        login_check = require_login()

        if login_check:
            return login_check

        # ----------------------------------------------------
        # Panchayat lookup
        # ----------------------------------------------------

        panchayat = db.session.get(
            Panchayat,
            panchayat_id
        )

        if not panchayat:

            return jsonify({
                "success": False,
                "error": "Panchayat not found"
            }), 404

        # ----------------------------------------------------
        # Authorization
        # ----------------------------------------------------

        access_error = check_panchayat_access(
            panchayat
        )

        if access_error:
            return access_error

        try:

            # ------------------------------------------------
            # Generate AI prediction
            # ------------------------------------------------

            result = predict_panchayat_weather(
                panchayat_id
            )

            # ------------------------------------------------
            # Store prediction
            # ------------------------------------------------

            prediction = PanchayatPrediction(

                panchayat_id=panchayat_id,

                target_time=result[
                    "target_time"
                ],

                temperature_c=result[
                    "temperature_c"
                ],

                rainfall_mm=result[
                    "rainfall_mm"
                ],

                humidity_percent=result[
                    "humidity_percent"
                ],

                wind_speed_kmh=result[
                    "wind_speed_kmh"
                ],

                model_name=result[
                    "model_name"
                ],

                model_version=result[
                    "model_version"
                ],

                source=result[
                    "source"
                ],

                data_type=result[
                    "data_type"
                ]
            )

            db.session.add(
                prediction
            )

            db.session.commit()

            # ------------------------------------------------
            # Response
            # ------------------------------------------------

            return jsonify({

                "success": True,

                "message":
                    "Panchayat-level AI prediction "
                    "generated successfully.",

                "panchayat": {

                    "id":
                        panchayat.id,

                    "name":
                        panchayat.name,

                    "latitude":
                        panchayat.latitude,

                    "longitude":
                        panchayat.longitude

                },

                "prediction":
                    prediction.to_dict()

            }), 200

        except Exception as exc:

            db.session.rollback()

            return jsonify({

                "success": False,

                "error":
                    "AI prediction failed",

                "details":
                    str(exc)

            }), 500


    # ========================================================
    # AI downscaling
    # AI PREDICTION HISTORY
    # ========================================================

    @app.get(
        "/api/ai/panchayat/<int:panchayat_id>/predictions"
    )
    def ai_prediction_history(panchayat_id):

        # ----------------------------------------------------
        # Authentication
        # ----------------------------------------------------

        login_check = require_login()

        if login_check:
            return login_check

        # ----------------------------------------------------
        # Panchayat lookup
        # ----------------------------------------------------

        panchayat = db.session.get(
            Panchayat,
            panchayat_id
        )

        if not panchayat:

            return jsonify({
                "success": False,
                "error": "Panchayat not found"
            }), 404

        # ----------------------------------------------------
        # Authorization
        # ----------------------------------------------------

        access_error = check_panchayat_access(
            panchayat
        )

        if access_error:
            return access_error

        # ----------------------------------------------------
        # Fetch prediction history
        # ----------------------------------------------------

        predictions = (
            PanchayatPrediction.query
            .filter_by(
                panchayat_id=panchayat_id
            )
            .order_by(
                PanchayatPrediction.target_time.desc()
            )
            .limit(50)
            .all()
        )

        return jsonify({

            "success": True,

            "panchayat": {

                "id":
                    panchayat.id,

                "name":
                    panchayat.name

            },

            "count":
                len(predictions),

            "data_type":
                "MODELLED_PREDICTION",

            "predictions": [

                prediction.to_dict()

                for prediction
                in predictions

            ]

        }), 200

    # ========================================================
    # Risk assessment
    # ========================================================

    def build_panchayat_risk_payload(panchayat):

        feature = PanchayatFeature.query.filter_by(
            panchayat_id=panchayat.id
        ).first()

        prediction = (
            PanchayatPrediction.query
            .filter_by(panchayat_id=panchayat.id)
            .order_by(PanchayatPrediction.target_time.desc())
            .first()
        )

        if not prediction:
            return {
                "panchayat": {
                    "id": panchayat.id,
                    "name": panchayat.name,
                    "latitude": panchayat.latitude,
                    "longitude": panchayat.longitude,
                },
                "status": "NO_PREDICTION",
                "risk": None,
                "prediction": None,
            }

        risk = calculate_risk(
            temperature_c=prediction.temperature_c,
            rainfall_mm=prediction.rainfall_mm,
            humidity_percent=prediction.humidity_percent,
            wind_speed_kmh=prediction.wind_speed_kmh,
            flood_susceptibility=(
                feature.historical_flood_susceptibility
                if feature else 0
            ),
        )

        return {
            "panchayat": {
                "id": panchayat.id,
                "name": panchayat.name,
                "latitude": panchayat.latitude,
                "longitude": panchayat.longitude,
            },
            "status": "RISK_AVAILABLE",
            "risk": risk,
            "prediction": prediction.to_dict(),
            "features": {
                "flood_susceptibility": (
                    feature.historical_flood_susceptibility
                    if feature else None
                ),
                "terrain_type": feature.terrain_type if feature else None,
                "land_cover": feature.land_cover if feature else None,
            },
        }


    @app.get("/api/risk/panchayat/<int:panchayat_id>")
    def panchayat_risk(panchayat_id):

        login_check = require_login()
        if login_check:
            return login_check

        panchayat = db.session.get(Panchayat, panchayat_id)
        if not panchayat:
            return jsonify({"success": False, "error": "Panchayat not found"}), 404

        access_error = check_panchayat_access(panchayat)
        if access_error:
            return access_error

        payload = build_panchayat_risk_payload(panchayat)
        return jsonify({"success": True, **payload}), 200


    @app.get("/api/risk/overview")
    def risk_overview():

        login_check = require_login()
        if login_check:
            return login_check

        user = get_current_user()
        query = Panchayat.query

        # Government sees the monitoring map for all Panchayats.
        if user.role == "panchayat_official":
            if not user.panchayat:
                return jsonify({"success": True, "panchayats": []}), 200
            query = query.filter_by(id=user.panchayat.id)
        elif user.role == "citizen":
            if not user.panchayat:
                return jsonify({"success": True, "panchayats": []}), 200
            query = query.filter_by(id=user.panchayat.id)

        records = []
        for panchayat in query.order_by(Panchayat.name).all():
            records.append(build_panchayat_risk_payload(panchayat))

        return jsonify({
            "success": True,
            "count": len(records),
            "panchayats": records,
        }), 200


    # ========================================================
    # Alerts & response workflow
    # ========================================================

    def alert_access(alert, user):
        """Return a response on access failure, otherwise None."""
        if user.role == "government":
            return None
        if user.panchayat and user.panchayat.id == alert.panchayat_id:
            return None
        return jsonify({"success": False, "error": "Access denied for this alert."}), 403

    def build_alert_payload(alert, include_recipients=False):
        payload = alert.to_dict()
        responses = (
            PanchayatResponse.query
            .filter_by(alert_id=alert.id)
            .order_by(PanchayatResponse.updated_at.desc())
            .all()
        )
        payload["responses"] = [item.to_dict() for item in responses]
        payload["response_status"] = responses[0].status if responses else "PENDING"

        # Expose aggregate notification state to every authorized alert viewer,
        # while keeping individual recipient details restricted to operational users.
        recipients = list(alert.recipients)
        payload["notification_summary"] = {
            "total": len(recipients),
            "in_app_queued": sum(1 for item in recipients if item.channel == "IN_APP" and item.delivery_status == "QUEUED"),
            "sms_ready_queued": sum(1 for item in recipients if item.channel == "SMS_READY" and item.delivery_status == "QUEUED"),
            "accepted": sum(1 for item in recipients if item.delivery_status == "ACCEPTED"),
            "delivered": sum(1 for item in recipients if item.delivery_status == "DELIVERED"),
            "dry_run": sum(1 for item in recipients if item.delivery_status == "DRY_RUN"),
            "failed": sum(1 for item in recipients if item.delivery_status == "FAILED"),
        }
        # Build a compact operational timeline from persisted alert/response state.
        timeline = [{
            "event": "ALERT_GENERATED",
            "status": alert.status,
            "at": alert.generated_at.isoformat() if alert.generated_at else None,
            "user_name": None,
            "note": None,
        }]
        for item in responses:
            timeline.append({
                "event": item.status,
                "status": item.status,
                "at": item.updated_at.isoformat() if item.updated_at else None,
                "user_name": item.user.name if item.user else None,
                "note": item.note,
            })
        if alert.resolved_at and not any(item.status == "RESOLVED" for item in responses):
            timeline.append({
                "event": "ALERT_RESOLVED",
                "status": "RESOLVED",
                "at": alert.resolved_at.isoformat(),
                "user_name": None,
                "note": None,
            })
        timeline.sort(key=lambda item: item.get("at") or "", reverse=True)
        payload["timeline"] = timeline
        if include_recipients:
            payload["recipients"] = [item.to_dict() for item in recipients]
        return payload

    def alert_action_text(level):
        actions = {
            "ORANGE": "Prepare locally: inspect vulnerable locations and keep appropriate local resources ready.",
            "RED": "Priority attention: review applicable official procedures and inspect vulnerable or low-lying locations.",
        }
        return actions.get(level, "Continue local weather monitoring and follow applicable official instructions.")

    @app.get("/api/alerts")
    def list_alerts():
        login_check = require_login()
        if login_check:
            return login_check

        user = get_current_user()
        query = Alert.query
        if user.role != "government":
            if not user.panchayat:
                return jsonify({"success": True, "count": 0, "alerts": []}), 200
            query = query.filter_by(panchayat_id=user.panchayat.id)

        status_filter = request.args.get("status", "ACTIVE").upper()
        if status_filter != "ALL":
            query = query.filter_by(status=status_filter)

        alerts = query.order_by(Alert.generated_at.desc()).limit(50).all()
        return jsonify({
            "success": True,
            "count": len(alerts),
            "alerts": [build_alert_payload(alert) for alert in alerts],
        }), 200

    @app.get("/api/alerts/history")
    def alert_history():
        """Return persisted alert history for the current user's authorized scope."""
        login_check = require_login()
        if login_check:
            return login_check

        user = get_current_user()
        query = Alert.query
        if user.role != "government":
            if not user.panchayat:
                return jsonify({"success": True, "count": 0, "alerts": [], "events": []}), 200
            query = query.filter_by(panchayat_id=user.panchayat.id)

        status_filter = request.args.get("status", "ALL").upper()
        if status_filter in {"ACTIVE", "RESOLVED"}:
            query = query.filter_by(status=status_filter)

        limit = min(max(request.args.get("limit", 100, type=int), 1), 200)
        alerts = query.order_by(Alert.generated_at.desc()).limit(limit).all()
        payloads = [build_alert_payload(alert) for alert in alerts]

        # Flatten alert lifecycle events for an operational audit-style view.
        events = []
        for alert in payloads:
            for event in alert.get("timeline", []):
                events.append({
                    "alert_id": alert["id"],
                    "panchayat": alert.get("panchayat"),
                    "severity": alert.get("severity"),
                    **event,
                })
        events.sort(key=lambda item: item.get("at") or "", reverse=True)

        return jsonify({
            "success": True,
            "count": len(payloads),
            "alerts": payloads,
            "events": events[:300],
        }), 200


    @app.post("/api/alerts/generate/<int:panchayat_id>")
    def generate_alert(panchayat_id):
        login_check = require_login()
        if login_check:
            return login_check
        user = get_current_user()
        if user.role not in {"government", "panchayat_official"}:
            return jsonify({"success": False, "error": "Only authorized operational users can generate alerts."}), 403

        panchayat = db.session.get(Panchayat, panchayat_id)
        if not panchayat:
            return jsonify({"success": False, "error": "Panchayat not found"}), 404
        access_error = check_panchayat_access(panchayat)
        if access_error:
            return access_error

        payload = build_panchayat_risk_payload(panchayat)
        risk = payload.get("risk")
        prediction = payload.get("prediction")
        if not risk or not prediction:
            return jsonify({"success": False, "error": "Generate a current AI prediction before creating a screening alert."}), 400

        level = str(risk.get("level", "")).upper()
        if level not in {"ORANGE", "RED"}:
            return jsonify({
                "success": False,
                "error": f"Alert generation is limited to ORANGE/RED screening levels. Current level: {level or 'NO DATA'}.",
                "risk": risk,
            }), 400

        existing = (
            Alert.query
            .filter_by(panchayat_id=panchayat.id, prediction_id=prediction["id"], status="ACTIVE")
            .first()
        )
        if existing:
            return jsonify({
                "success": True,
                "created": False,
                "message": "An active alert already exists for this prediction.",
                "alert": build_alert_payload(existing, include_recipients=True),
            }), 200

        alert = Alert(
            panchayat_id=panchayat.id,
            prediction_id=prediction["id"],
            severity=level,
            alert_type="WEATHER_RISK_SCREENING",
            title=f"MEGHDRISHTI SCREENING ALERT • {level}",
            message=(
                f"{panchayat.name} has a {level} screening risk with score "
                f"{float(risk.get('score', 0)):.1f}/100. {alert_action_text(level)} "
                "This is a modelled screening indicator, not an official IMD warning."
            ),
            risk_score=float(risk.get("score", 0)),
            status="ACTIVE",
        )
        db.session.add(alert)
        db.session.flush()

        # Create a notification queue that is ready for an SMS provider later.
        recipients = User.query.filter(User.is_active.is_(True)).filter(
            User.role.in_(["government", "panchayat_official"])
        ).all()
        recipients = [r for r in recipients if r.role == "government" or r.panchayat_id == panchayat.id]
        for recipient in recipients:
            db.session.add(AlertRecipient(alert_id=alert.id, user_id=recipient.id, channel="IN_APP", delivery_status="QUEUED"))
            if recipient.mobile:
                db.session.add(AlertRecipient(alert_id=alert.id, user_id=recipient.id, channel="SMS_READY", delivery_status="QUEUED"))

        db.session.commit()
        return jsonify({
            "success": True,
            "created": True,
            "message": "Screening alert created and notification queue prepared.",
            "alert": build_alert_payload(alert, include_recipients=True),
        }), 201

    @app.post("/api/alerts/<int:alert_id>/acknowledge")
    def acknowledge_alert(alert_id):
        login_check = require_login()
        if login_check:
            return login_check
        user = get_current_user()
        if user.role not in {"government", "panchayat_official"}:
            return jsonify({"success": False, "error": "Citizen accounts are read-only for alert acknowledgement."}), 403

        alert = db.session.get(Alert, alert_id)
        if not alert:
            return jsonify({"success": False, "error": "Alert not found"}), 404
        access_error = alert_access(alert, user)
        if access_error:
            return access_error

        note = (request.get_json(silent=True) or {}).get("note", "").strip()[:1000]
        response = (
            PanchayatResponse.query
            .filter_by(alert_id=alert.id, panchayat_id=alert.panchayat_id, user_id=user.id)
            .first()
        )
        if not response:
            response = PanchayatResponse(alert_id=alert.id, panchayat_id=alert.panchayat_id, user_id=user.id)
            db.session.add(response)
        response.status = "ACKNOWLEDGED"
        response.note = note or response.note
        response.updated_at = datetime.utcnow()
        db.session.commit()

        return jsonify({"success": True, "message": "Alert acknowledgement recorded.", "response": response.to_dict()}), 200

    @app.post("/api/alerts/<int:alert_id>/resolve")
    def resolve_alert(alert_id):
        login_check = require_login()
        if login_check:
            return login_check
        user = get_current_user()
        if user.role not in {"government", "panchayat_official"}:
            return jsonify({"success": False, "error": "Only operational users can resolve alerts."}), 403
        alert = db.session.get(Alert, alert_id)
        if not alert:
            return jsonify({"success": False, "error": "Alert not found"}), 404
        access_error = alert_access(alert, user)
        if access_error:
            return access_error

        note = (request.get_json(silent=True) or {}).get("note", "").strip()[:1000]
        alert.status = "RESOLVED"
        alert.resolved_at = datetime.utcnow()
        response = PanchayatResponse(
            alert_id=alert.id,
            panchayat_id=alert.panchayat_id,
            user_id=user.id,
            status="RESOLVED",
            note=note or "Alert resolved by operational user.",
        )
        db.session.add(response)
        db.session.commit()
        return jsonify({"success": True, "message": "Alert marked resolved.", "alert": build_alert_payload(alert)}), 200

    @app.post("/api/alerts/<int:alert_id>/send-sms")
    def send_alert_sms(alert_id):
        """Send queued SMS_READY recipients through the configured provider."""
        login_check = require_login()
        if login_check:
            return login_check

        user = get_current_user()
        if user.role not in {"government", "panchayat_official"}:
            return jsonify({"success": False, "error": "Only operational users can send SMS notifications."}), 403

        alert = db.session.get(Alert, alert_id)
        if not alert:
            return jsonify({"success": False, "error": "Alert not found."}), 404

        access_error = alert_access(alert, user)
        if access_error:
            return access_error

        config = provider_status()
        if not config["dry_run"] and not config["configured"]:
            return jsonify({
                "success": False,
                "error": "SMS provider is not configured. Set SMS_PROVIDER and FAST2SMS_API_KEY in .env before sending.",
                "provider": config,
            }), 503

        queued = [
            item for item in alert.recipients
            if item.channel == "SMS_READY" and item.delivery_status == "QUEUED"
        ]
        if not queued:
            return jsonify({
                "success": True,
                "sent": 0,
                "failed": 0,
                "message": "No queued SMS-ready recipients remain for this alert.",
            }), 200

        message = build_sms_message(alert)
        sent = 0
        failed = 0
        results = []
        for recipient in queued:
            mobile = normalize_indian_mobile(recipient.user.mobile if recipient.user else None)
            if not mobile:
                recipient.delivery_status = "FAILED"
                failed += 1
                results.append({"recipient_id": recipient.id, "status": "FAILED", "error": "Recipient has no valid Indian mobile number."})
                continue

            result = send_sms(mobile, message)
            if result.get("success"):
                if result.get("status") == "DRY_RUN":
                    # Keep the queue state honest in simulation mode; no external delivery occurred.
                    recipient.delivery_status = "DRY_RUN"
                else:
                    recipient.delivery_status = "ACCEPTED"
                    # Fast2SMS accepted the request; this is not proof of handset delivery.
                    recipient.delivered_at = datetime.utcnow()
                    sent += 1
                results.append({"recipient_id": recipient.id, "status": result.get("status"), "message": result.get("message")})
            else:
                recipient.delivery_status = "FAILED"
                failed += 1
                results.append({"recipient_id": recipient.id, "status": "FAILED", "error": result.get("error")})

        db.session.commit()
        return jsonify({
            "success": failed == 0,
            "sent": sent,
            "failed": failed,
            "dry_run": config["dry_run"],
            "provider": config["provider"],
            "message": "SMS request processed; Fast2SMS acceptance is not handset delivery." if not config["dry_run"] else "SMS delivery simulated; no external SMS was sent.",
            "results": results,
        }), 200

    @app.get("/api/alerts/<int:alert_id>/notifications")
    def alert_notifications(alert_id):
        login_check = require_login()
        if login_check:
            return login_check
        user = get_current_user()
        if user.role not in {"government", "panchayat_official"}:
            return jsonify({"success": False, "error": "Notification delivery details are restricted to operational users."}), 403
        alert = db.session.get(Alert, alert_id)
        if not alert:
            return jsonify({"success": False, "error": "Alert not found"}), 404
        access_error = alert_access(alert, user)
        if access_error:
            return access_error
        recipients = list(alert.recipients)
        summary = {
            "total": len(recipients),
            "queued": sum(1 for item in recipients if item.delivery_status == "QUEUED"),
            "accepted": sum(1 for item in recipients if item.delivery_status == "ACCEPTED"),
            "delivered": sum(1 for item in recipients if item.delivery_status == "DELIVERED"),
            "dry_run": sum(1 for item in recipients if item.delivery_status == "DRY_RUN"),
            "failed": sum(1 for item in recipients if item.delivery_status == "FAILED"),
            "channels": {
                "in_app": sum(1 for item in recipients if item.channel == "IN_APP"),
                "sms_ready": sum(1 for item in recipients if item.channel == "SMS_READY"),
            },
        }
        return jsonify({"success": True, "summary": summary, "notifications": [item.to_dict() for item in recipients]}), 200

    # ========================================================
    # LOGOUT
    # ========================================================

    @app.get("/logout")
    def logout():

        session.clear()

        return redirect(
            url_for("index")
        )

    # ========================================================
    # HEALTH CHECK
    # ========================================================

    @app.get("/api/health")
    def health():

        return jsonify({

            "status": "healthy",

            "project": "MeghDrishti",

            "stage": "Final demonstration build",

            "timestamp":
                datetime.utcnow().isoformat() + "Z",
        })

    # ========================================================
    # SYSTEM STATUS
    # ========================================================

    @app.get("/api/system")
    def system_status():

        return jsonify({

            "application": "running",

            "database": "configured",

            "authentication": "implemented",

            "rbac": "implemented",

            "location_hierarchy": "implemented",

            "weather": "implemented",

            "weather_source": "Open-Meteo",

            "weather_storage": "implemented",

            "ai_downscaling": "implemented",

            "risk_engine": "implemented",

            "dashboards": "implemented",

            "alerts": "implemented",
        })

    # ========================================================
    # ERROR HANDLERS
    # ========================================================

    @app.errorhandler(403)
    def forbidden(error):

        if request.path.startswith("/api/"):

            return jsonify({
                "error": "Forbidden",
                "message": "You do not have permission to access this resource.",
            }), 403

        return (
            render_template(
                "base.html",
                error_code=403,
                error_message="Access denied.",
            ),
            403,
        )

    @app.errorhandler(404)
    def not_found(error):

        if request.path.startswith("/api/"):

            return jsonify({
                "error": "Not found",
                "message": "The requested resource does not exist.",
            }), 404

        return (
            render_template(
                "base.html",
                error_code=404,
                error_message="Page not found.",
            ),
            404,
        )

    # ========================================================
    # DATABASE INITIALIZATION
    # ========================================================

    with app.app_context():

        db.create_all()

    return app


# ============================================================
# APPLICATION INSTANCE
# ============================================================

app = create_app()


# ============================================================
# DEVELOPMENT SERVER
# ============================================================

if __name__ == "__main__":

    app.run(

        host=os.getenv(
            "HOST",
            "127.0.0.1",
        ),

        port=int(
            os.getenv(
                "PORT",
                "5000",
            )
        ),

        debug=os.getenv(
            "FLASK_DEBUG",
            "0",
        ) == "1",
    )
