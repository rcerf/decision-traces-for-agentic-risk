import importlib.util
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ABLATION_PATH = ROOT / "src" / "stage_ablation.py"

spec = importlib.util.spec_from_file_location("stage_ablation", ABLATION_PATH)
stage_ablation = importlib.util.module_from_spec(spec)
assert spec.loader is not None
sys.modules[spec.name] = stage_ablation
spec.loader.exec_module(stage_ablation)


class StageAblationTest(unittest.TestCase):
    def test_full_pipeline_detects_more_than_final_only(self):
        report = stage_ablation.run_ablation(ROOT / "data" / "runs")

        final_only = report["conditions"]["final_only"]
        full_pipeline = report["conditions"]["full_pipeline"]

        self.assertLess(final_only["detected_runs"], full_pipeline["detected_runs"])
        self.assertLess(final_only["total_events"], full_pipeline["total_events"])

    def test_trajectory_condition_catches_connector_boundary(self):
        report = stage_ablation.run_ablation(ROOT / "data" / "runs")
        trajectory = report["conditions"]["ingress_trajectory_final"]["per_run"]["RUN-003"]

        self.assertTrue(trajectory["risk_present"])
        self.assertEqual(trajectory["first_detection_stage"], "trajectory")
        self.assertIn("connector_data_boundary", trajectory["categories"])


if __name__ == "__main__":
    unittest.main()
