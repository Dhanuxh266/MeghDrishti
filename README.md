# MEGHDRISHTI

### AI-Powered Panchayat-Level Weather Intelligence & Early Warning System

**SIH Problem Statement:** SIH26074 -- Weather Forecast Downscaling\
**Project Type:** MVP / Proof of Concept

------------------------------------------------------------------------

## Overview

**MeghDrishti** is an AI-powered weather intelligence system designed to
demonstrate how regional weather information can be converted into
**Panchayat-level predictions, risk assessment, and localized alerts**.

The MVP focuses on one complete workflow:

**Weather Data → AI Downscaling → Panchayat Prediction → Risk Assessment
→ Alert → Local Response**

------------------------------------------------------------------------

## MVP Features

-   **Role-Based Login** --- Government Official, Panchayat Official,
    and Citizen
-   **Panchayat Hierarchy** --- State → District → Taluka → Panchayat
-   **Weather Integration** --- Current and forecast weather data
-   **AI Downscaling** --- ML-based Panchayat-level weather prediction
-   **Risk Assessment** --- Explainable Green / Yellow / Orange / Red
    risk levels
-   **Interactive Map** --- Panchayat locations and risk visualization
-   **Early Alerts** --- In-app alerts with response tracking
-   **Three Dashboards** --- Government, Panchayat Official, and Citizen
-   **SMS-Ready Architecture** --- Optional notification provider
    integration

------------------------------------------------------------------------

## How It Works

``` text
Weather Data
     ↓
Local Panchayat Features
     ↓
AI Downscaling Model
     ↓
Panchayat-Level Prediction
     ↓
Risk Assessment
     ↓
Alert Generation
     ↓
Panchayat Response
     ↓
Citizen Awareness
```

------------------------------------------------------------------------

## AI Component

The MVP uses machine-learning models such as:

-   Random Forest
-   Linear Regression
-   XGBoost (when available)

### Inputs

-   Temperature
-   Rainfall
-   Humidity
-   Wind Speed
-   Latitude / Longitude
-   Elevation
-   Environmental features
-   Historical weather
-   Temporal features

### Outputs

-   Panchayat-level temperature
-   Rainfall
-   Humidity
-   Wind speed

Model performance is evaluated using **MAE, RMSE and R²**.

------------------------------------------------------------------------

## Risk Assessment

The predicted weather conditions are passed through an explainable
rule-based risk engine.

  Level           Score Meaning
  ----------- --------- ----------------
  🟢 Green        0--24 Low Risk
  🟡 Yellow      25--49 Watch
  🟠 Orange      50--74 High Risk
  🔴 Red        75--100 Very High Risk

> These are MVP screening levels and are not official IMD warning
> thresholds.

------------------------------------------------------------------------

## Dashboards

### Government Official

Central monitoring of Panchayats, risks, alerts and responses.

### Panchayat Official

Local weather, predictions, risk status, alerts and acknowledgement.

### Citizen

Localized weather, risk information, warnings and safety guidance.

------------------------------------------------------------------------

## Technology Stack

**Backend:** Python, Flask, SQLAlchemy\
**Database:** PostgreSQL (production) / SQLite (local MVP fallback)\
**AI/ML:** Pandas, NumPy, Scikit-learn, XGBoost\
**Frontend:** HTML, CSS, JavaScript\
**Maps:** Leaflet, OpenStreetMap\
**Weather:** Open-Meteo API\
**Notifications:** Optional Fast2SMS integration

------------------------------------------------------------------------

## Project Structure

``` text
meghdrishti/
├── app.py
├── requirements.txt
├── api/
├── models/
├── services/
├── ml/
├── scripts/
├── data/
└── frontend/
```

------------------------------------------------------------------------

## Setup

### 1. Create virtual environment

``` bash
python -m venv .venv
```

### 2. Activate it

**Windows**

``` bash
.venv\Scriptsctivate
```

**Linux / macOS**

``` bash
source .venv/bin/activate
```

### 3. Install dependencies

``` bash
pip install -r requirements.txt
```

### 4. Configure environment

Create `.env` from `.env.example` and add the required configuration.

For local development, SQLite can be used as the default database.

For PostgreSQL, set:

``` env
DATABASE_URL=postgresql://USERNAME:PASSWORD@HOST:PORT/DATABASE_NAME
```

### 5. Run

``` bash
python app.py
```

Open:

``` text
http://127.0.0.1:5000
```

------------------------------------------------------------------------

## PostgreSQL

For production deployment, MeghDrishti uses **PostgreSQL** as the
persistent database.

Set the following environment variable:

``` env
DATABASE_URL=postgresql://USERNAME:PASSWORD@HOST:PORT/DATABASE_NAME
```

The application automatically uses the configured `DATABASE_URL` and
initializes the required SQLAlchemy tables when the application starts.

> PostgreSQL is recommended for deployed environments because the
> application requires persistent database storage. SQLite remains
> available as a local development fallback.

------------------------------------------------------------------------

## Deployment

### Vercel Deployment

The current project is configured for deployment on **Vercel** using the
Flask entry point:

``` text
api/index.py
```

The repository includes:

``` text
vercel.json
api/index.py
```

### Deployment Steps

1.  Push the project to GitHub.
2.  Open Vercel and import the GitHub repository.
3.  Select the project root containing `app.py` and `vercel.json`.
4.  Deploy the project using the included Vercel configuration.
5.  Add the required environment variables in **Vercel → Project
    Settings → Environment Variables**.

Recommended production variables:

``` env
APP_ENV=production
SECRET_KEY=<strong-random-secret>
DATABASE_URL=postgresql://USERNAME:PASSWORD@HOST:PORT/DATABASE_NAME
```

Optional variables can also be configured for services such as SMS
notifications and trusted hosts.

6.  Redeploy the project after adding or changing environment variables.
7.  Open the generated Vercel deployment URL to access MeghDrishti.

### Current Deployment

**Platform:** Vercel\
**Deployment URL:** https://meghdrishti-nine.vercel.app

The deployed application uses the production configuration and
PostgreSQL persistence through the `DATABASE_URL` environment variable.

> Do not commit `.env`, database credentials, API keys, or secret values
> to the GitHub repository.

------------------------------------------------------------------------

## Demo Scope

The current version is an **MVP demonstration**, not a production
meteorological warning system.

Demonstration data may be simulated where Panchayat-level historical or
environmental datasets are unavailable. It should not be interpreted as
official government data.

For production deployment, the system would require validated government
datasets, official geographical boundaries, model calibration,
independent meteorological validation, secure infrastructure and
authorized warning/telecom integrations.

------------------------------------------------------------------------

## MVP Goal

MeghDrishti demonstrates the feasibility of combining **AI weather
downscaling, Panchayat-level context, explainable risk assessment and
localized early-warning workflows** in a single platform.

> **From regional weather data to actionable Panchayat-level
> intelligence.**
