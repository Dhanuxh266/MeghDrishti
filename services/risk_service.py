"""Risk assessment engine for MeghDrishti.

This is a transparent rule-based screening index, not an official IMD warning
algorithm. It combines the latest modelled Panchayat weather prediction with
local flood susceptibility and returns an explainable 0-100 risk score.
"""

from __future__ import annotations

from typing import Any, Dict, Optional


def _piecewise(value: float, points: list[tuple[float, float]]) -> float:
    """Linear interpolation between risk points, clamped to [0, 100]."""
    if value <= points[0][0]:
        return points[0][1]
    for (x0, y0), (x1, y1) in zip(points, points[1:]):
        if value <= x1:
            ratio = (value - x0) / (x1 - x0)
            return y0 + ratio * (y1 - y0)
    return points[-1][1]


def classify_risk(score: float) -> Dict[str, Any]:
    score = max(0.0, min(100.0, float(score)))
    if score < 25:
        return {"level": "GREEN", "label": "Low Risk", "color": "green"}
    if score < 50:
        return {"level": "YELLOW", "label": "Watch", "color": "yellow"}
    if score < 75:
        return {"level": "ORANGE", "label": "High Risk", "color": "orange"}
    return {"level": "RED", "label": "Very High Risk", "color": "red"}


def calculate_risk(
    *,
    temperature_c: Optional[float],
    rainfall_mm: Optional[float],
    humidity_percent: Optional[float],
    wind_speed_kmh: Optional[float],
    flood_susceptibility: Optional[float],
) -> Dict[str, Any]:
    """Calculate an explainable weighted hazard screening score.

    Weights:
      rainfall 45%, wind 20%, humidity 10%, temperature extremes 10%,
      local flood susceptibility 15%.
    """
    temp = float(temperature_c or 0)
    rain = max(0.0, float(rainfall_mm or 0))
    humidity = max(0.0, min(100.0, float(humidity_percent or 0)))
    wind = max(0.0, float(wind_speed_kmh or 0))
    flood = max(0.0, min(1.0, float(flood_susceptibility or 0)))

    rainfall_component = _piecewise(
        rain,
        [(0, 0), (10, 10), (25, 30), (50, 60), (100, 85), (150, 100)],
    )
    wind_component = _piecewise(
        wind,
        [(0, 0), (20, 10), (40, 30), (60, 60), (80, 85), (100, 100)],
    )
    humidity_component = _piecewise(
        humidity,
        [(0, 0), (70, 0), (85, 35), (95, 70), (100, 100)],
    )

    # Temperature is treated as an extreme-weather contribution only.
    if temp >= 45:
        temperature_component = 100.0
    elif temp >= 40:
        temperature_component = 75.0
    elif temp >= 37:
        temperature_component = 35.0
    elif temp <= 2:
        temperature_component = 100.0
    elif temp <= 5:
        temperature_component = 75.0
    elif temp <= 8:
        temperature_component = 35.0
    else:
        temperature_component = 0.0

    flood_component = flood * 100.0

    weighted = (
        rainfall_component * 0.45
        + wind_component * 0.20
        + humidity_component * 0.10
        + temperature_component * 0.10
        + flood_component * 0.15
    )

    classification = classify_risk(weighted)

    components = {
        "rainfall": {
            "value": round(rain, 2),
            "score": round(rainfall_component, 1),
            "weight_percent": 45,
        },
        "wind": {
            "value": round(wind, 2),
            "score": round(wind_component, 1),
            "weight_percent": 20,
        },
        "humidity": {
            "value": round(humidity, 1),
            "score": round(humidity_component, 1),
            "weight_percent": 10,
        },
        "temperature_extreme": {
            "value": round(temp, 2),
            "score": round(temperature_component, 1),
            "weight_percent": 10,
        },
        "flood_susceptibility": {
            "value": round(flood, 3),
            "score": round(flood_component, 1),
            "weight_percent": 15,
        },
    }

    # Rank the largest weighted contributors for the explanation.
    weighted_contributors = [
        ("Rainfall intensity", rainfall_component * 0.45),
        ("Wind speed", wind_component * 0.20),
        ("Humidity", humidity_component * 0.10),
        ("Temperature extreme", temperature_component * 0.10),
        ("Flood susceptibility", flood_component * 0.15),
    ]
    weighted_contributors.sort(key=lambda item: item[1], reverse=True)

    explanations = []
    for name, contribution in weighted_contributors:
        if contribution >= 8:
            explanations.append(f"{name} is contributing to the risk score.")
    if not explanations:
        explanations.append("No major hazard driver is currently elevated.")

    return {
        "score": round(weighted, 1),
        **classification,
        "components": components,
        "explanation": explanations[:3],
        "method": "Rule-based weighted hazard screening index",
        "warning": "Screening indicator only; not an official IMD warning threshold.",
    }
