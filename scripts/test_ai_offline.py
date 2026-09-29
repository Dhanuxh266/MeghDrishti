"""Offline runtime-model verification. No Flask server or network required."""
from pathlib import Path
import json
import joblib
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
MODEL = ROOT / "ml/models/random_forest.joblib"
METRICS = ROOT / "ml/models/model_metrics.json"
assert MODEL.exists(), "Runtime Random Forest model is missing"
assert METRICS.exists(), "Model metrics are missing"
model = joblib.load(MODEL)
assert hasattr(model, "predict"), "Runtime model is not predictive"
metrics = json.loads(METRICS.read_text(encoding="utf-8"))
assert isinstance(metrics, dict) and metrics, "Model metrics are empty"

# Infer feature count from the fitted estimator and run a shape-safe smoke prediction.
feature_count = getattr(model, "n_features_in_", None)
assert feature_count and feature_count > 0, "Model feature metadata is missing"
dataset = ROOT / "data/training/meghdrishti_training_dataset.csv"
df = pd.read_csv(dataset)
feature_names = list(getattr(model, "feature_names_in_", []))
assert feature_names, "Model feature names are missing"
sample = df[feature_names].iloc[[0]].copy()
prediction = model.predict(sample)
assert len(prediction) == 1, "Runtime prediction failed"
print(f"Runtime Random Forest: PASS ({feature_count} features)")
print("No external network calls were made.")
