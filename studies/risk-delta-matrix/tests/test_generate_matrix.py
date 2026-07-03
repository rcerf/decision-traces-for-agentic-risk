import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path


MODULE_PATH = Path(__file__).resolve().parents[1] / "src" / "generate_matrix.py"
spec = importlib.util.spec_from_file_location("generate_matrix", MODULE_PATH)
generate_matrix = importlib.util.module_from_spec(spec)
assert spec.loader is not None
sys.modules[spec.name] = generate_matrix
spec.loader.exec_module(generate_matrix)


class RiskDeltaMatrixTests(unittest.TestCase):
    def test_generates_probe_now_cells(self):
        deltas = generate_matrix.load_json(Path(__file__).resolve().parents[1] / "data" / "capability_deltas.json")
        risks = generate_matrix.load_json(Path(__file__).resolve().parents[1] / "data" / "risk_classes.json")
        cells = generate_matrix.generate_cells(deltas, risks)

        self.assertTrue(any(cell["status"] == "probe_now" for cell in cells))
        self.assertTrue(any("Persistent memory" in cell["delta"] for cell in cells))

    def test_report_writes_markdown(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            output = Path(tmpdir) / "risk_delta_matrix.md"
            report = generate_matrix.generate(output)

        self.assertIn("# Risk Delta Matrix", report)
        self.assertIn("Safe Probe", report)


if __name__ == "__main__":
    unittest.main()

