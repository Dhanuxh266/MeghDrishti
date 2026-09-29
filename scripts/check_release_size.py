"""Check that the deployable project remains comfortably below 500 MB."""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
LIMIT = 500 * 1024 * 1024

total = sum(p.stat().st_size for p in ROOT.rglob('*') if p.is_file())
print(f"Release tree size: {total / (1024 * 1024):.2f} MB")
if total >= LIMIT:
    print("FAIL: release tree is not below 500 MB")
    sys.exit(1)
print("PASS: release tree is below 500 MB")
