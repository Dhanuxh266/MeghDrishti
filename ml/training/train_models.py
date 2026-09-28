import os
import sys
import json

import joblib
import numpy as np
import pandas as pd

from sklearn.pipeline import Pipeline
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.multioutput import MultiOutputRegressor
from sklearn.metrics import (
    mean_absolute_error,
    mean_squared_error,
    r2_score
)


PROJECT_ROOT = os.path.abspath(
    os.path.join(
        os.path.dirname(__file__),
        "../.."
    )
)

sys.path.insert(
    0,
    PROJECT_ROOT
)


from ml.preprocessing.features import (
    load_training_data,
    create_preprocessor
)


DATASET = os.path.join(
    PROJECT_ROOT,
    "data",
    "training",
    "meghdrishti_training_dataset.csv"
)


MODEL_DIR = os.path.join(
    PROJECT_ROOT,
    "ml",
    "models"
)


METRICS_FILE = os.path.join(
    MODEL_DIR,
    "model_metrics.json"
)


TARGETS = [
    "target_temperature_c",
    "target_rainfall_mm",
    "target_humidity_percent",
    "target_wind_speed_kmh"
]


def rmse(y_true, y_pred):

    return np.sqrt(
        mean_squared_error(
            y_true,
            y_pred
        )
    )


def evaluate(
    y_true,
    y_pred
):

    results = {}


    for index, target in enumerate(TARGETS):

        results[target] = {

            "MAE":
                float(
                    mean_absolute_error(
                        y_true.iloc[:, index],
                        y_pred[:, index]
                    )
                ),

            "RMSE":
                float(
                    rmse(
                        y_true.iloc[:, index],
                        y_pred[:, index]
                    )
                ),

            "R2":
                float(
                    r2_score(
                        y_true.iloc[:, index],
                        y_pred[:, index]
                    )
                )
        }


    return results


def average_score(metrics):

    values = []

    for target in TARGETS:

        values.append(
            metrics[target]["MAE"]
        )

    return float(
        np.mean(values)
    )


def train():

    os.makedirs(
        MODEL_DIR,
        exist_ok=True
    )


    df, X, y = load_training_data(
        DATASET
    )


    # --------------------------------------------------------
    # CHRONOLOGICAL DATE-BASED SPLIT
    # --------------------------------------------------------
    # All Panchayat rows belonging to a date stay in the same
    # split. This prevents the same forecast date appearing in
    # both training and validation sets.

    dates = pd.to_datetime(df["date"])
    order = np.argsort(dates.values)

    X = X.iloc[order].reset_index(drop=True)
    y = y.iloc[order].reset_index(drop=True)
    df = df.iloc[order].reset_index(drop=True)
    dates = pd.to_datetime(df["date"])

    unique_dates = dates.drop_duplicates().sort_values().reset_index(drop=True)
    split_date_index = max(1, int(len(unique_dates) * 0.80))
    if split_date_index >= len(unique_dates):
        split_date_index = len(unique_dates) - 1

    cutoff_date = unique_dates.iloc[split_date_index]
    train_mask = dates < cutoff_date
    test_mask = dates >= cutoff_date

    if train_mask.sum() == 0 or test_mask.sum() == 0:
        raise ValueError("Unable to create non-empty chronological train/validation splits.")

    X_train = X.loc[train_mask].reset_index(drop=True)
    X_test = X.loc[test_mask].reset_index(drop=True)
    y_train = y.loc[train_mask].reset_index(drop=True)
    y_test = y.loc[test_mask].reset_index(drop=True)

    train_start = dates.loc[train_mask].min().date().isoformat()
    train_end = dates.loc[train_mask].max().date().isoformat()
    validation_start = dates.loc[test_mask].min().date().isoformat()
    validation_end = dates.loc[test_mask].max().date().isoformat()


    # --------------------------------------------------------
    # MODELS
    # --------------------------------------------------------

    models = {

        "linear_regression":
            LinearRegression(),

        "random_forest":
            RandomForestRegressor(
                n_estimators=250,
                max_depth=12,
                min_samples_leaf=2,
                random_state=42,
                n_jobs=-1
            )

    }


    # --------------------------------------------------------
    # XGBOOST
    # --------------------------------------------------------

    try:

        from xgboost import XGBRegressor


        models["xgboost"] = (
            XGBRegressor(
                n_estimators=250,
                max_depth=5,
                learning_rate=0.05,
                subsample=0.85,
                colsample_bytree=0.85,
                objective="reg:squarederror",
                random_state=42,
                n_jobs=4
            )
        )

    except Exception as exc:

        print(
            "XGBoost unavailable:"
        )

        print(
            str(exc)
        )


    metrics = {}


    # --------------------------------------------------------
    # TRAIN
    # --------------------------------------------------------

    for name, estimator in models.items():

        print()
        print(
            f"Training {name}..."
        )


        preprocessor = create_preprocessor()


        pipeline = Pipeline(

            steps=[

                (
                    "preprocessing",
                    preprocessor
                ),

                (
                    "model",

                    MultiOutputRegressor(
                        estimator
                    )
                )

            ]
        )


        pipeline.fit(
            X_train,
            y_train
        )


        predictions = pipeline.predict(
                X_test
            )


        model_metrics = evaluate(
                y_test,
                predictions
            )


        metrics[name] = {

            "targets":
                model_metrics,

            "average_mae":
                average_score(
                    model_metrics
                )
        }


        model_path = os.path.join(
            MODEL_DIR,
            f"{name}.joblib"
        )


        joblib.dump(
            pipeline,
            model_path
        )


        print(
            f"Average MAE: "
            f"{metrics[name]['average_mae']:.4f}"
        )


    # --------------------------------------------------------
    # MODEL SELECTION
    # --------------------------------------------------------

    selected_model = min(

        metrics,

        key=lambda name:
            metrics[name][
                "average_mae"
            ]
    )


    print()
    print(
        "=" * 60
    )

    print(
        "MODEL COMPARISON"
    )

    print(
        "=" * 60
    )


    for name, result in metrics.items():

        print(
            f"{name:20s}"
            f" MAE = "
            f"{result['average_mae']:.4f}"
        )


    print()
    print(
        f"SELECTED MODEL: "
        f"{selected_model}"
    )


    # --------------------------------------------------------
    # SAVE METADATA
    # --------------------------------------------------------

    metadata = {

        "selected_model":
            selected_model,

        "model_version":
            "meghdrishti-rf-2026-demo",

        "dataset":
            "SIMULATED_DEMO_TRAINING",

        "split":
            "chronological 80% dates / 20% dates",

        "train_date_range":
            f"{train_start} -> {train_end}",

        "validation_date_range":
            f"{validation_start} -> {validation_end}",

        "targets":
            TARGETS,

        "metrics":
            metrics
    }


    with open(
        METRICS_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            metadata,
            file,
            indent=4
        )


    selected_source = os.path.join(
        MODEL_DIR,
        f"{selected_model}.joblib"
    )


    selected_destination = os.path.join(
        MODEL_DIR,
        "selected_model.joblib"
    )


    joblib.dump(
        joblib.load(
            selected_source
        ),
        selected_destination
    )


    print()
    print(
        f"Saved selected model:"
    )

    print(
        selected_destination
    )


if __name__ == "__main__":

    train()