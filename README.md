MEGHDRISHTI

AI-Powered Panchayat-Level Weather Intelligence & Early Warning System

Smart India Hackathon (SIH) Problem Statement:
SIH26074 – Weather Forecast Downscaling
Project Type: Demonstration MVP
Domain: AI for Weather, Rainfall & Disaster Prediction

1. What is MeghDrishti?

MeghDrishti is an MVP that demonstrates how coarse-scale weather
information can be transformed into Panchayat-level weather
intelligence and used to support localized risk awareness and
early-warning workflows.

The core idea is:

Coarse Weather Data → AI Downscaling → Panchayat-Level Prediction →
Risk Assessment → Alert → Local Response

Instead of treating weather information only at a broad regional level,
MeghDrishti combines weather information with Panchayat-specific
geographical, environmental and historical features to produce localized
modelled weather estimates.

The MVP then uses those predictions in an explainable risk-screening
engine and presents the result through role-based dashboards for:

Government Officials

Panchayat Officials

Citizens

2. MVP Objective

The objective of this MVP is not to build a nationwide production
weather forecasting system.

The objective is to provide a complete, working and demonstrable proof
of concept showing the end-to-end feasibility of Panchayat-level
weather intelligence.

The MVP demonstrates five major capabilities:

Local weather intelligence

Retrieves weather information for Panchayat locations.

Stores current observations and forecast information.

AI-based downscaling

Uses a trained machine-learning model to estimate
Panchayat-level weather variables.

Combines coarse weather inputs with local geographical,
environmental and historical features.

Explainable risk assessment

Converts modelled weather conditions into a transparent 0--100
screening score.

Classifies the result as Green, Yellow, Orange or Red.

Early-warning workflow

Generates alerts for affected Panchayats.

Allows Panchayat officials to acknowledge and respond to alerts.

Role-based decision dashboards

Government monitoring

Panchayat-level operational view

Citizen-facing localized information

3. MVP Workflow

                WEATHER DATA
                     │
                     ▼
          Weather API / Stored Data
                     │
                     ▼
          Coarse Weather Information
                     │
          ┌──────────┴──────────┐
          │                     │
          ▼                     ▼
   Panchayat Geography     Historical Weather
   & Environmental Data          Data
          │                     │
          └──────────┬──────────┘
                     ▼
             AI DOWNSCALING
                     │
                     ▼
        Panchayat-Level Prediction
      ┌────────┬────────┬────────┬────────┐
      │ Temp.  │ Rain   │ Humid. │ Wind   │
      └────────┴────────┴────────┴────────┘
                     │
                     ▼
             RISK ASSESSMENT
                     │
                     ▼
          0–100 Screening Score
                     │
                     ▼
          GREEN / YELLOW / ORANGE / RED
                     │
                     ▼
               ALERT ENGINE
                     │
          ┌──────────┴──────────┐
          ▼                     ▼
    Dashboard Alert       SMS-ready Workflow
          │
          ▼
   Panchayat Acknowledgement
          │
          ▼
       Response Note
          │
          ▼
        Resolution
          │
          ▼
        Alert History

4. What is included in the MVP?

4.1 Authentication & Role-Based Access

The application provides a unified login system with backend-enforced
role access.

Supported roles

Role                                Purpose

Government Official                 Monitor Panchayats, risks, alerts
and operational activity

Panchayat Official                  Monitor assigned Panchayat
conditions and respond to alerts

The user's role is stored server-side and access restrictions are
enforced by the backend.

Citizen registration

Citizens can register with:

Name

Mobile number

Optional email

Panchayat

Password

The selected Panchayat determines the user's associated State → District
→ Taluka → Panchayat hierarchy.

5. Panchayat Location Hierarchy

The MVP models the administrative hierarchy as:

State
  └── District
       └── Taluka
            └── Panchayat

The packaged demonstration uses a Maharashtra-based demonstration
geography.

The database stores Panchayat-level attributes such as:

Latitude

Longitude

Elevation

Population

Area

Local environmental features

Historical flood susceptibility

The architecture can be extended to additional districts, talukas and
Panchayats.

6. Weather Data Layer

MeghDrishti uses the Open-Meteo Forecast API for weather ingestion
in the demonstration application.

Weather information includes:

Current observations

Temperature

Feels-like temperature

Relative humidity

Rainfall / precipitation

Wind speed

Surface pressure

Weather code

Forecast information

Temperature

Apparent temperature

Humidity

Precipitation probability

Rainfall / precipitation

Wind speed

Pressure

Weather code

Weather data is associated with individual Panchayat locations and
stored locally for use by the application and AI pipeline.

7. AI Downscaling Component

Why downscaling?

Large-scale weather forecasts do not directly represent the micro-level
conditions of every Panchayat.

The MVP therefore demonstrates a machine-learning approach that uses:

Coarse weather features

Temperature

Rainfall

Humidity

Wind speed

Panchayat geographical/environmental features

Latitude

Longitude

Elevation

Distance from water

Historical flood susceptibility

Vegetation index

Land cover

Terrain type

Historical weather features

Historical temperature

Historical rainfall

Historical humidity

Historical wind speed

Historical pressure

Previous temperature

Previous rainfall

Previous humidity

Temporal features

Month

Day of year

AI outputs

The model predicts:

Panchayat temperature

Panchayat rainfall

Panchayat humidity

Panchayat wind speed

The prediction is stored with:

Prediction timestamp

Target timestamp

Model name

Model version

Data source/type

8. Model Training & Selection

The project includes a reproducible machine-learning training pipeline.

The MVP compares:

Linear Regression

Random Forest

XGBoost, when available

The training pipeline uses a chronological date-based split so that
records from the same date are kept in the same partition.

This is preferable to randomly mixing observations across training and
validation data for a time-dependent weather demonstration.

Evaluation metrics

For each target variable, the project calculates:

MAE --- Mean Absolute Error

RMSE --- Root Mean Squared Error

R² --- Coefficient of Determination

The model with the lowest average MAE is selected by the training
pipeline.

The packaged project contains trained model artifacts and evaluation
metrics so that the demonstration can run without retraining every time.

9. Scientific Integrity of the MVP

The AI component is intended to be a meaningful demonstration of the
downscaling concept, not a claim of operational meteorological
forecasting accuracy.

The project therefore distinguishes between:

Modelled prediction

Produced by the trained machine-learning model.

Live weather data

Retrieved from the configured weather source.

Demonstration/simulated data

Used where real Panchayat-level historical or environmental observations
are not available in the MVP.

The project does not claim that its demonstration dataset represents
official government meteorological data.

Production deployment would require:

Validated Panchayat-level observations

Larger historical datasets

Better spatial/environmental features

Independent validation

Calibration

Continuous monitoring

Domain and meteorological validation

10. Risk Assessment Engine

The MVP contains an explainable rule-based risk screening engine.

It combines:

Factor                              Weight

Rainfall                               45%
Wind                                   20%
Humidity                               10%
Temperature extremes                   10%
Historical flood susceptibility        15%

The weighted result produces a score between 0 and 100.

Risk classification

   Score Level    Meaning in MVP

 0--24.9 GREEN    Low Risk
25--49.9 YELLOW   Watch
50--74.9 ORANGE   High Risk
 75--100 RED      Very High Risk

The application also identifies the major contributors to the score so
that the result is explainable.

Important limitation

These risk levels are screening indicators for the MVP.

They are not official IMD warning thresholds, government disaster
declarations, or certified emergency warnings.

11. Alert & Response Workflow

When the system identifies an elevated screening risk, the MVP supports
an operational alert workflow.

Risk Assessment
      ↓
Alert Generation
      ↓
Affected Panchayat
      ↓
Recipients
      ↓
In-App Alert
      ↓
Panchayat Official Acknowledgement
      ↓
Response Note
      ↓
Resolution
      ↓
Alert History

The database maintains alert-related records including:

Alert severity

Risk score

Alert status

Affected Panchayat

Recipients

Delivery status

Panchayat response

Response notes

Resolution information

12. SMS-Ready Notification Architecture

The notification layer is designed so that the MVP can operate without
sending real SMS by default.

Default behavior

SMS is disabled unless explicitly configured.

Dry-run mode

A dry-run configuration can simulate the SMS handoff without contacting
an external provider.

Optional Fast2SMS integration

The project contains an optional Fast2SMS integration for MVP/internal
testing.

The implementation supports:

Provider configuration

Indian mobile-number validation

Quick SMS route

Optional DLT configuration

Provider response handling

Dry-run mode

A successful provider response means the provider accepted the request.
It does not independently prove that the SMS reached the recipient's
handset.

For production government communication, approved telecom/provider
routes, templates, DLT requirements and operational controls would need
to be implemented.

13. Three Dashboard Concepts

Government Dashboard

Designed for centralized monitoring.

Provides visibility into:

Panchayat conditions

Risk levels

Active alerts

Weather information

Risk map

Alert activity

Response status

Panchayat Official Dashboard

Focused on the assigned Panchayat.

Provides:

Local weather

Panchayat prediction

Risk status

Alert information

Acknowledge action

Response notes

Resolution workflow

Citizen Dashboard

Designed for localized public information.

Provides:

Panchayat weather

Forecast information

Risk status

Warnings

Safety guidance

Localized information based on the registered Panchayat

14. Interactive Map

The application includes an interactive map for Panchayat-level
visualization.

The map is designed to communicate:

Panchayat locations

Risk status

Localized weather context

Geographic distribution of alerts

The current MVP focuses on Panchayat points and demonstration geography.
Detailed official Panchayat boundary polygons can be added in a
production expansion.

15. Technology Stack

Backend

Python

Flask

Flask-SQLAlchemy

Werkzeug

Requests

python-dotenv

Database

SQLite for the packaged MVP demonstration

SQLAlchemy ORM

The architecture can be migrated to PostgreSQL/PostGIS for
production-scale deployment.

AI / Data

Pandas

NumPy

scikit-learn

XGBoost

Joblib

Frontend

HTML

CSS

JavaScript

Leaflet

OpenStreetMap

External service

Open-Meteo weather API

Optional Fast2SMS notification provider

16. Project Structure

meghdrishti_final/
│
├── app.py
├── extensions.py
├── requirements.txt
├── .env.example
│
├── data/
│   └── training/
│       └── meghdrishti_training_dataset.csv
│
├── instance/
│   └── meghdrishti.db
│
├── models/
│   ├── user.py
│   ├── location.py
│   ├── weather.py
│   ├── historical_weather.py
│   ├── panchayat_features.py
│   ├── prediction.py
│   └── alert.py
│
├── services/
│   ├── ai_service.py
│   ├── weather_services.py
│   ├── risk_service.py
│   └── notification_service.py
│
├── ml/
│   ├── preprocessing/
│   ├── training/
│   ├── evaluation/
│   └── models/
│       ├── selected_model.joblib
│       ├── random_forest.joblib
│       ├── linear_regression.joblib
│       ├── xgboost.joblib
│       └── model_metrics.json
│
├── scripts/
│   ├── seed_demo.py
│   ├── seed_weather_demo.py
│   ├── test_ai.py
│   ├── test_risk.py
│   └── test_notifications.py
│
└── frontend/
    ├── templates/
    │   ├── base.html
    │   ├── login.html
    │   ├── register.html
    │   └── dashboard.html
    │
    └── static/
        ├── css/
        │   └── style.css
        ├── js/
        │   └── app.js
        └── assets/

17. Local Setup

Windows

py -3.11 -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
python app.py

Linux / macOS

python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python app.py

Then open:

http://127.0.0.1:5000

18. Demo Data

The packaged MVP contains a demonstration SQLite database and
training/model artifacts.

The demo environment includes:

Maharashtra location hierarchy

Ratnagiri demonstration geography

Panchayat records

Demo users

Weather records

Panchayat features

Modelled predictions

Risk/alert workflow data

Where data is marked as demonstration/simulated, it should not be
interpreted as an official government dataset.

19. Demo Login Accounts

The seeded demonstration accounts are:

Government Official

Email: gov@meghdrishti.local
Password: Gov@12345

Panchayat Official

Email: panchayat@meghdrishti.local
Password: Panchayat@123

Citizen

Email: citizen@meghdrishti.local
Password: Citizen@123

These credentials are intended only for the local demonstration
environment.

Do not reuse them in a public deployment.

20. Suggested SIH Demonstration Flow

A concise demonstration can follow this sequence:

Step 1 --- Login

Show the role-based login screen.

Step 2 --- Government monitoring

Open the Government Dashboard and show:

Panchayat overview

Risk distribution

Map

Active alerts

Step 3 --- Panchayat intelligence

Select a Panchayat and show:

Current weather

Forecast

AI-generated Panchayat prediction

Model information

Step 4 --- Explain the AI

Explain that the model combines:

Coarse Weather
+
Panchayat Geography
+
Environmental Features
+
Historical Weather
+
Temporal Features
        ↓
Panchayat-Level Prediction

Step 5 --- Explain the risk

Show how the prediction feeds the rule-based screening engine.

Explain the main contributors to the risk score.

Step 6 --- Alert

Demonstrate the alert workflow.

Step 7 --- Panchayat response

Login as the Panchayat Official and:

View the alert

Acknowledge it

Add a response note

Resolve/update the response

Step 8 --- Citizen view

Login as the Citizen and show the localized:

Weather

Risk

Warning

Safety information

This demonstrates the complete chain:

Prediction → Risk → Alert → Response → Citizen Awareness

21. MVP Scope vs Future Production System

Included in this MVP

Role-based authentication

Government dashboard

Panchayat Official dashboard

Citizen dashboard

State → District → Taluka → Panchayat hierarchy

Panchayat weather ingestion

AI downscaling

Model comparison and evaluation

Panchayat-level predictions

Explainable risk screening

Risk visualization

Interactive map

Alert generation

Panchayat acknowledgement

Response workflow

Alert history

SMS-ready architecture

Optional Fast2SMS integration

Demonstration database

Demonstration ML artifacts

Not claimed as production functionality

Nationwide operational deployment

Official IMD integration

Official government warning issuance

Direct telecom Cell Broadcast integration

Production-grade disaster management certification

Fully validated Panchayat boundary datasets

National-scale meteorological forecasting

Calibrated operational warning thresholds

Large-scale distributed infrastructure

Production-grade MLOps

Guaranteed SMS handset delivery

22. Limitations & Scientific Disclaimer

MeghDrishti is an MVP/proof-of-concept system.

The model, risk engine and demonstration data are intended to show the
architecture and technical feasibility of Panchayat-level weather
intelligence.

The system should not be used as a substitute for:

Official meteorological forecasts

IMD warnings

Government disaster-management instructions

Certified emergency communication systems

The demonstration model requires further validation using real,
sufficiently large and representative Panchayat-level datasets before
any operational forecasting or warning use.

23. Production Roadmap

A production-oriented version could add:

Data

Validated government weather datasets

Dense Panchayat-level observations

Official administrative boundaries

DEM/elevation datasets

Satellite-derived land-cover and vegetation features

AI

Larger multi-year training datasets

Spatial-temporal modelling

Calibration

Uncertainty estimation

Independent validation

Continuous model monitoring

Risk

Domain-validated thresholds

Hydrological/flood models

Local vulnerability indices

Disaster-management authority validation

Infrastructure

PostgreSQL/PostGIS

Production WSGI deployment

HTTPS

Background jobs

Monitoring and logging

Scalable APIs

Alerts

Approved SMS/DLT workflows

Government notification systems

Telecom/Cell Broadcast integration where authorized

Delivery confirmation/webhooks

24. Security Notes

Before public deployment:

Replace the development SECRET_KEY.

Never commit .env or API keys.

Disable Flask debug mode.

Use HTTPS.

Use a production WSGI server.

Use secure session configuration.

Use a managed production database.

Rotate external API credentials if exposed.

Apply appropriate access controls and audit logging.

Review SMS provider and DLT credentials carefully.

25. Final MVP Statement

MeghDrishti demonstrates an end-to-end Panchayat-level weather
intelligence workflow:

Weather Data
     ↓
Local Feature Integration
     ↓
AI Downscaling
     ↓
Panchayat Prediction
     ↓
Explainable Risk Screening
     ↓
Localized Alert
     ↓
Panchayat Response
     ↓
Citizen Awareness

The MVP's primary contribution is the integration of AI-based weather
downscaling, Panchayat-level contextual features, explainable risk
assessment and role-based early-warning operations into one
demonstrable system.

It is intentionally designed as a technically meaningful and
scientifically transparent MVP, providing a foundation that can be
expanded with validated government data, advanced geospatial modelling
and authorized operational warning infrastructure.