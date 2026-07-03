import importlib.util
import json
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TRIAGE_PATH = ROOT / "src" / "signal_triage.py"

spec = importlib.util.spec_from_file_location("signal_triage", TRIAGE_PATH)
signal_triage = importlib.util.module_from_spec(spec)
assert spec.loader is not None
sys.modules[spec.name] = signal_triage
spec.loader.exec_module(signal_triage)


class SignalTriageTest(unittest.TestCase):
    def setUp(self):
        self.signals = json.loads((ROOT / "data" / "source_signals" / "sample_public_signals.json").read_text())

    def test_sample_signals_validate(self):
        for signal in self.signals:
            with self.subTest(signal=signal["signal_id"]):
                self.assertEqual(signal_triage.validate_signal(signal), [])

    def test_social_signal_routes_to_review_and_no_raw_reproduction(self):
        summary = signal_triage.summarize(self.signals)

        self.assertIn("SIG-006", summary["review_queue"])
        self.assertIn("SIG-006", summary["do_not_reproduce_raw_details"])

    def test_generated_signal_ids_are_allowed(self):
        signal = dict(self.signals[0])
        signal["signal_id"] = "SIG-ARXIV-ABC123"

        self.assertEqual(signal_triage.validate_signal(signal), [])

    def test_highest_priority_backlog_contains_actionable_authoritative_signal(self):
        summary = signal_triage.summarize(self.signals)
        first = summary["probe_backlog"][0]

        self.assertGreaterEqual(first["priority"], 80)
        self.assertFalse(first["review_required"])

    def test_function_call_gap_becomes_probe_candidate(self):
        summary = signal_triage.summarize(self.signals)
        matching = [
            item for item in summary["probe_backlog"]
            if "function_call_malfunction" in item["risk_categories"]
        ]

        self.assertEqual(len(matching), 1)
        self.assertEqual(matching[0]["expected_detection_stage"], "trajectory")


if __name__ == "__main__":
    unittest.main()
