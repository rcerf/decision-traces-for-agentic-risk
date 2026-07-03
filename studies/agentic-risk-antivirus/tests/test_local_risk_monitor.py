import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path


MODULE_PATH = Path(__file__).resolve().parents[1] / "src" / "local_risk_monitor.py"
spec = importlib.util.spec_from_file_location("local_risk_monitor", MODULE_PATH)
local_risk_monitor = importlib.util.module_from_spec(spec)
assert spec.loader is not None
sys.modules[spec.name] = local_risk_monitor
spec.loader.exec_module(local_risk_monitor)

ANON_PATH = Path(__file__).resolve().parents[1] / "src" / "anonymize_events.py"
anon_spec = importlib.util.spec_from_file_location("anonymize_events", ANON_PATH)
anonymize_events = importlib.util.module_from_spec(anon_spec)
assert anon_spec.loader is not None
sys.modules[anon_spec.name] = anonymize_events
anon_spec.loader.exec_module(anonymize_events)


class LocalRiskMonitorTests(unittest.TestCase):
    def test_sample_sessions_detect_known_risks(self):
        result = local_risk_monitor.scan_file(
            Path(__file__).resolve().parents[1] / "data" / "sample_sessions.json",
            Path(__file__).resolve().parents[1] / "rules" / "risk_signatures.json",
        )

        categories = {event["category"] for event in result["events"]}
        self.assertIn("prompt_injection", categories)
        self.assertIn("missing_approval", categories)
        self.assertIn("connector_data_boundary", categories)
        self.assertIn("unstable_action_selection", categories)
        self.assertIn("social_engineering", categories)

    def test_anonymized_output_excludes_raw_evidence_excerpt(self):
        result = local_risk_monitor.scan_file(
            Path(__file__).resolve().parents[1] / "data" / "sample_sessions.json",
            Path(__file__).resolve().parents[1] / "rules" / "risk_signatures.json",
        )
        with tempfile.TemporaryDirectory() as tmpdir:
            event_path = Path(tmpdir) / "events.json"
            event_path.write_text(__import__("json").dumps(result))
            aggregate = anonymize_events.aggregate(anonymize_events.load_result(event_path))

        rendered = __import__("json").dumps(aggregate)
        self.assertNotIn("external-review@example.com", rendered)
        self.assertIn("event_fingerprints", aggregate)


if __name__ == "__main__":
    unittest.main()

