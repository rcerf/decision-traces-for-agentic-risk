"""Tests for the AgentDojo -> decision-trace adapter.

Verifies:
- Every produced trace passes the repo's trace validator (reused, not re-implemented).
- AgentDojo semantics map correctly: security=False -> high + approval gate;
  security=True -> low + no gate; baselines are skipped.
- No message content / raw injection text leaks into a trace (the adapter only
  ever reads structural fields, so trace text must not contain fixture bodies).
"""
from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "demo"))
sys.path.insert(0, str(REPO / "studies" / "benchmark-adapter" / "src"))

from validate_traces import validate_trace  # noqa: E402
import agentdojo_to_trace as adapter  # noqa: E402

RUNS_DIR = REPO / "studies" / "benchmark-adapter" / "data" / "agentdojo_runs"


class TestAdapter(unittest.TestCase):
    def setUp(self) -> None:
        self.traces = adapter.convert_dir(RUNS_DIR, start_index=8, next_review="2026-07-30")

    def test_produces_traces(self) -> None:
        # 3 fixtures, 1 baseline -> 2 risk traces
        self.assertEqual(len(self.traces), 2)

    def test_all_traces_validate(self) -> None:
        for t in self.traces:
            errors = validate_trace(t)
            self.assertEqual(errors, [], f"{t['trace_id']} failed validation: {errors}")

    def test_successful_injection_is_high_and_gated(self) -> None:
        highs = [t for t in self.traces if t["severity"] == "high"]
        self.assertTrue(highs, "expected at least one high-severity successful-injection trace")
        for t in highs:
            self.assertTrue(t["human_approval"]["required"])
            self.assertNotEqual(t["human_approval"]["approval_gate"], "none")
            self.assertEqual(t["mitigation_status"], "needs_review")

    def test_baseline_is_skipped(self) -> None:
        baseline = json.loads((RUNS_DIR / "workspace__it0__none.json").read_text())
        self.assertTrue(adapter.is_baseline(baseline))

    def test_no_raw_message_content_leaks(self) -> None:
        # Sentinel strings that appear in the raw AgentDojo message bodies but must
        # never appear in a structural trace.
        forbidden = ["mark.black-2134@gmail.com", "<thinking>", "Networking event"]
        for t in self.traces:
            blob = json.dumps(t)
            for s in forbidden:
                self.assertNotIn(s, blob, f"raw fixture content '{s}' leaked into {t['trace_id']}")


if __name__ == "__main__":
    unittest.main()
