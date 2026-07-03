import importlib.util
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PATH = ROOT / "src" / "ingest_x.py"

spec = importlib.util.spec_from_file_location("ingest_x", PATH)
ingest_x = importlib.util.module_from_spec(spec)
assert spec.loader is not None
sys.path.insert(0, str(PATH.parent))
sys.modules[spec.name] = ingest_x
try:
    spec.loader.exec_module(ingest_x)
finally:
    sys.path.pop(0)

signal_triage_path = ROOT / "src" / "signal_triage.py"
triage_spec = importlib.util.spec_from_file_location("signal_triage_for_x_tests", signal_triage_path)
signal_triage = importlib.util.module_from_spec(triage_spec)
assert triage_spec.loader is not None
sys.modules[triage_spec.name] = signal_triage
triage_spec.loader.exec_module(signal_triage)


SAMPLE_PAYLOAD = {
    "data": [
        {
            "id": "123",
            "author_id": "u1",
            "created_at": "2026-07-02T12:00:00.000Z",
            "text": "Public discussion of a new AI agent guardrail bypass pattern.",
        }
    ],
    "includes": {
        "users": [
            {"id": "u1", "username": "researcher", "name": "Researcher"}
        ]
    },
}


class XAdapterTest(unittest.TestCase):
    def test_payload_to_signals_is_review_gated_and_valid(self):
        signals = ingest_x.payload_to_signals(
            SAMPLE_PAYLOAD,
            source_name="X saved payload",
            default_categories=["jailbreak_motif"],
            default_surfaces=["ingress", "final_output"],
            raw_detail_policy="do_not_reproduce",
        )

        self.assertEqual(len(signals), 1)
        self.assertEqual(signal_triage.validate_signal(signals[0]), [])
        self.assertEqual(signals[0]["source_tier"], 3)
        self.assertEqual(signals[0]["raw_detail_policy"], "do_not_reproduce")
        self.assertIn("x.com/researcher/status/123", signals[0]["source_url"])

    def test_safe_summary_truncates_long_posts(self):
        text = "x" * 300
        self.assertLessEqual(len(ingest_x.safe_summary(text)), 220)


if __name__ == "__main__":
    unittest.main()
