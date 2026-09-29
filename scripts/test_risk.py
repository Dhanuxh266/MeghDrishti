"""Offline risk-engine verification."""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from services.risk_service import calculate_risk

def run_case(name, **kwargs):
    result = calculate_risk(**kwargs)
    print(f"{name}: {result['score']}/100 -> {result['level']} ({result['label']})")
    assert 0 <= result['score'] <= 100
    assert result['level'] in {"GREEN", "YELLOW", "ORANGE", "RED"}
    assert result['components']

run_case("Normal conditions", temperature_c=24.8, rainfall_mm=2.7, humidity_percent=71, wind_speed_kmh=13.8, flood_susceptibility=0.62)
run_case("Heavy-rain scenario", temperature_c=25, rainfall_mm=110, humidity_percent=94, wind_speed_kmh=55, flood_susceptibility=0.75)
run_case("Severe multi-hazard scenario", temperature_c=42, rainfall_mm=150, humidity_percent=98, wind_speed_kmh=95, flood_susceptibility=0.90)
print("Risk engine checks: PASS")
