"""Offline Day-8A release checks. No network or SMS calls are made."""
from pathlib import Path
import json
import os
import re
import sys

ROOT = Path(__file__).resolve().parents[1]

def check(condition, message):
    if not condition:
        raise AssertionError(message)

app = (ROOT / "app.py").read_text(encoding="utf-8")
example = (ROOT / ".env.example").read_text(encoding="utf-8")
vercel = json.loads((ROOT / "vercel.json").read_text(encoding="utf-8"))
requirements = (ROOT / "requirements.txt").read_text(encoding="utf-8")
gitignore = (ROOT / ".gitignore").read_text(encoding="utf-8")

check(not (ROOT / ".env").exists(), ".env must not be included in the release archive")
check((ROOT / ".env.example").exists(), ".env.example is missing")
check("SECRET_KEY must be set" in app, "Production secret-key guard is missing")
check('SESSION_COOKIE_HTTPONLY' in app, "HTTP-only session cookie setting is missing")
check('SESSION_COOKIE_SECURE' in app, "Secure session cookie setting is missing")
check('/api/readiness' in app, "Readiness endpoint is missing")
check(vercel.get("builds"), "Vercel build configuration is missing")
check((ROOT / "api/index.py").exists(), "Vercel Flask entry point is missing")
check("gunicorn" in requirements, "Gunicorn dependency is missing")
check((ROOT / "Procfile").exists(), "Procfile is missing")
check((ROOT / "render.yaml").exists(), "Render configuration is missing")
check(".env" in gitignore, ".env is not ignored")
check("FAST2SMS_API_KEY=" in example, "Safe SMS configuration template is missing")

# Guard against accidentally packaging a concrete provider key in text files.
for path in ROOT.rglob("*"):
    if not path.is_file() or path.suffix.lower() not in {".py", ".txt", ".md", ".json", ".yaml", ".yml", ".env", ".js"}:
        continue
    if "__pycache__" in path.parts:
        continue
    text = path.read_text(encoding="utf-8", errors="ignore")
    for line in text.splitlines():
        if line.startswith("FAST2SMS_API_KEY="):
            check(line.strip() == "FAST2SMS_API_KEY=", f"Concrete Fast2SMS key found in {path}")
        if line.startswith("SECRET_KEY="):
            value = line.split("=", 1)[1].strip()
            check(value in {"", "<strong-random-secret>"}, f"Concrete SECRET_KEY found in {path}")

print("Day-8A offline release checks: PASS")
print("No external network or SMS calls were made.")
