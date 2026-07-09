"""Pytest configuration: add src/ to sys.path for all tests in this study."""

import sys
from pathlib import Path

# Insert src/ so tests can do: from mock_tools import ...
SRC = Path(__file__).resolve().parents[1] / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))
