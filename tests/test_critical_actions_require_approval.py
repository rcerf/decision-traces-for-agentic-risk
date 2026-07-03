import importlib.util
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
VALIDATOR_PATH = ROOT / "demo" / "validate_traces.py"

spec = importlib.util.spec_from_file_location("validate_traces", VALIDATOR_PATH)
validate_traces = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(validate_traces)


class CriticalActionApprovalTest(unittest.TestCase):
    def test_high_and_critical_traces_have_approval_gates(self):
        for path in sorted((ROOT / "examples").glob("*.json")):
            with self.subTest(path=path.name):
                trace = json.loads(path.read_text())
                errors = validate_traces.validate_trace(trace)
                self.assertEqual(errors, [])

    def test_validator_flags_missing_high_risk_approval(self):
        trace = {
            "trace_id": "ART-999",
            "title": "unsafe synthetic trace",
            "source_signal": "synthetic_probe",
            "agentic_surface": "connector",
            "risk_category": "tool_overreach",
            "evidence": {
                "observed_behavior": "Agent prepares an external action.",
                "why_it_matters": "External side effect.",
                "open_questions": []
            },
            "confidence": "medium",
            "severity": "high",
            "recommended_action": "Add gate.",
            "owner": "Product",
            "mitigation_status": "proposed",
            "human_approval": {
                "required": False,
                "reason": "Missing control.",
                "approval_gate": "none"
            },
            "residual_risk": "Agent could act without confirmation.",
            "next_review": "2026-07-09"
        }

        errors = validate_traces.validate_trace(trace)
        self.assertIn("high/critical trace lacks human approval requirement", errors)
        self.assertIn("high/critical trace lacks approval gate", errors)


if __name__ == "__main__":
    unittest.main()
