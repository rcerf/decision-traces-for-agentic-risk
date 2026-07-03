import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path


MODULE_PATH = Path(__file__).resolve().parents[1] / "src" / "network_triage.py"
spec = importlib.util.spec_from_file_location("network_triage", MODULE_PATH)
network_triage = importlib.util.module_from_spec(spec)
assert spec.loader is not None
sys.modules[spec.name] = network_triage
spec.loader.exec_module(network_triage)


class OptInSignalSharingTests(unittest.TestCase):
    def test_high_uncertainty_side_effect_routes_to_patch_candidate(self):
        nodes = network_triage.load_nodes()
        summary = network_triage.summarize(nodes)

        routes = {event["event_id"]: event["route"] for event in summary["events"]}
        self.assertEqual(routes["EVT-001"], "auto_promote_patch_candidate")
        self.assertEqual(routes["EVT-003"], "aggregate_watch")

    def test_raw_fields_are_rejected(self):
        nodes = network_triage.load_nodes()
        nodes[0]["events"][0]["raw_prompt"] = "private"

        with self.assertRaises(ValueError):
            network_triage.summarize(nodes)

    def test_report_writes_markdown(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            output = Path(tmpdir) / "network.md"
            report = network_triage.generate(output_path=output)
            self.assertTrue(output.exists())

        self.assertIn("Opt-In Signal-Sharing Concept Assessment", report)
        self.assertIn("Privacy Invariants", report)


if __name__ == "__main__":
    unittest.main()
