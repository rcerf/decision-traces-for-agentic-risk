import importlib.util
import json
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SENTINEL_PATH = ROOT / "src" / "risk_sentinel.py"

spec = importlib.util.spec_from_file_location("risk_sentinel", SENTINEL_PATH)
risk_sentinel = importlib.util.module_from_spec(spec)
assert spec.loader is not None
sys.modules[spec.name] = risk_sentinel
spec.loader.exec_module(risk_sentinel)


def load_run(name: str) -> dict:
    return json.loads((ROOT / "data" / "runs" / name).read_text())


class RiskSentinelTest(unittest.TestCase):
    def test_indirect_injection_detected_at_ingress(self):
        report = risk_sentinel.analyze_run(load_run("run-001-indirect-injection.json"))

        self.assertTrue(report["risk_present"])
        self.assertEqual(report["first_detection_stage"], "ingress")
        self.assertIn("prompt_injection", report["categories"])
        self.assertIn("missing_approval", report["categories"])

    def test_benign_summary_has_no_events(self):
        report = risk_sentinel.analyze_run(load_run("run-002-benign-summary.json"))

        self.assertFalse(report["risk_present"])
        self.assertEqual(report["first_detection_stage"], "none")
        self.assertEqual(report["events"], [])

    def test_connector_boundary_detected_at_trajectory(self):
        report = risk_sentinel.analyze_run(load_run("run-003-connector-boundary.json"))

        self.assertTrue(report["risk_present"])
        self.assertEqual(report["first_detection_stage"], "trajectory")
        self.assertIn("connector_data_boundary", report["categories"])

    def test_final_secret_leak_is_critical(self):
        report = risk_sentinel.analyze_run(load_run("run-004-final-leakage.json"))

        self.assertTrue(report["risk_present"])
        self.assertEqual(report["first_detection_stage"], "final")
        self.assertIn("data_leakage", report["categories"])
        self.assertEqual(report["severity_counts"].get("critical"), 1)


if __name__ == "__main__":
    unittest.main()
