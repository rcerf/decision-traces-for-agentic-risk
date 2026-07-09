"""Pytest configuration: add harness src and study root to sys.path."""
import sys
from pathlib import Path

STUDY_ROOT = Path(__file__).resolve().parents[1]
HARNESS_SRC = STUDY_ROOT.parent / "detonation-harness" / "src"

for p in (str(HARNESS_SRC), str(STUDY_ROOT)):
    if p not in sys.path:
        sys.path.insert(0, p)
