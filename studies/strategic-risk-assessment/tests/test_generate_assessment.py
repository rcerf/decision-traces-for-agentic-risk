import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path


MODULE_PATH = (
    Path(__file__).resolve().parents[1]
    / "src"
    / "generate_assessment.py"
)
spec = importlib.util.spec_from_file_location("generate_assessment", MODULE_PATH)
generate_assessment = importlib.util.module_from_spec(spec)
assert spec.loader is not None
sys.modules[spec.name] = generate_assessment
spec.loader.exec_module(generate_assessment)


class GenerateAssessmentTests(unittest.TestCase):
    def test_risks_are_ranked_by_priority(self):
        items = generate_assessment.load_hypotheses(generate_assessment.DEFAULT_INPUT)
        ranked = generate_assessment.rank_hypotheses(items)

        scores = [risk.priority_score for risk in ranked]
        self.assertEqual(scores, sorted(scores, reverse=True))
        self.assertEqual(ranked[0].item["risk_id"], "SRA-001")

    def test_report_contains_caveat_and_product_run_command(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            output = Path(tmpdir) / "assessment.md"
            report = generate_assessment.generate(
                generate_assessment.DEFAULT_INPUT,
                output,
            )

        self.assertIn("It does not claim these risks are unknown to OpenAI", report)
        self.assertIn("python3 studies/strategic-risk-assessment/src/generate_assessment.py", report)
        self.assertIn("Cross-surface prompt injection", report)


if __name__ == "__main__":
    unittest.main()
