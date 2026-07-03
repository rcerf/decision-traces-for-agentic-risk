import importlib.util
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PATH = ROOT / "src" / "ingest_mit_tracker.py"

spec = importlib.util.spec_from_file_location("ingest_mit_tracker", PATH)
ingest_mit_tracker = importlib.util.module_from_spec(spec)
assert spec.loader is not None
sys.path.insert(0, str(PATH.parent))
sys.modules[spec.name] = ingest_mit_tracker
try:
    spec.loader.exec_module(ingest_mit_tracker)
finally:
    sys.path.pop(0)

signal_triage_path = ROOT / "src" / "signal_triage.py"
triage_spec = importlib.util.spec_from_file_location("signal_triage_for_mit_tests", signal_triage_path)
signal_triage = importlib.util.module_from_spec(triage_spec)
assert triage_spec.loader is not None
sys.modules[triage_spec.name] = signal_triage
triage_spec.loader.exec_module(signal_triage)


class MITTrackerAdapterTest(unittest.TestCase):
    def test_extract_insights_from_list_items(self):
        html = """
        <html><body><h3>Insights:</h3><ul>
          <li>There has been a clear rise in fraud, scams and targeted manipulation incidents.</li>
          <li>Navigation item should be ignored.</li>
          <li>The proportion of intentionally caused incidents has increased.</li>
        </ul></body></html>
        """
        insights = ingest_mit_tracker.extract_insights(html)

        self.assertEqual(len(insights), 2)
        self.assertIn("fraud", insights[0])

    def test_insights_become_valid_source_signals(self):
        signals = ingest_mit_tracker.insights_to_signals(
            ["Reported incidents involving scams have increased."],
            "https://airisk.mit.edu/ai-incident-tracker/incident-timeline",
        )

        self.assertEqual(len(signals), 1)
        self.assertEqual(signal_triage.validate_signal(signals[0]), [])
        self.assertEqual(signals[0]["source_name"], "MIT AI Incident Tracker")


if __name__ == "__main__":
    unittest.main()
