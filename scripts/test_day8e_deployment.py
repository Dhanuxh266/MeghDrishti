"""Offline deployment checks for Day 8E."""
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[1]

def require(path):
    assert (ROOT / path).exists(), f"Missing required deployment file: {path}"

for item in ["vercel.json", "render.yaml", "Procfile", "api/index.py", ".env.example"]:
    require(item)

config = json.loads((ROOT / "vercel.json").read_text())
assert config.get("version") == 2
assert config.get("builds") and config["builds"][0]["src"] == "api/index.py"

render = (ROOT / "render.yaml").read_text()
assert "DATABASE_URL" in render and "sync: false" in render
assert "SECRET_KEY" in render and "sync: false" in render

env = (ROOT / ".env.example").read_text()
assert "postgresql://" in env
assert "FAST2SMS_API_KEY=" in env

app = (ROOT / "app.py").read_text()
assert 'postgres://"' in app
assert "persistent_database" in app
assert "A persistent PostgreSQL DATABASE_URL is required" in app

for secret_name in ("FAST2SMS_API_KEY", "SECRET_KEY"):
    if (ROOT / ".env").exists():
        raise AssertionError("Concrete .env must not be included in the release")

print("Day-8E deployment checks: PASS")
