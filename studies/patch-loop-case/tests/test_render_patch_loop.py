import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path


MODULE_PATH = Path(__file__).resolve().parents[1] / "src" / "render_patch_loop.py"
spec = importlib.util.spec_from_file_location("render_patch_loop", MODULE_PATH)
render_patch_loop = importlib.util.module_from_spec(spec)
assert spec.loader is not None
sys.modules[spec.name] = render_patch_loop
spec.loader.exec_module(render_patch_loop)


class PatchLoopRenderTests(unittest.TestCase):
    def test_report_contains_patch_and_residual_monitor(self):
        case = render_patch_loop.load_case()
        report = render_patch_loop.render(case)

        self.assertIn("Patch Object", report)
        self.assertIn("Residual Monitor", report)
        self.assertIn("No raw exploit content is preserved", report)

    def test_report_excludes_raw_exploit_markers(self):
        report = render_patch_loop.render(render_patch_loop.load_case()).lower()

        self.assertNotIn("ignore previous instructions", report)
        self.assertNotIn("jailbreak prompt", report)
        self.assertNotIn("step-by-step exploit", report)

    def test_report_writes_markdown(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            output = Path(tmpdir) / "patch_loop.md"
            report = render_patch_loop.generate(output_path=output)
            self.assertTrue(output.exists())

        self.assertIn("Agent-On-Agent Probe To Patch Loop", report)


if __name__ == "__main__":
    unittest.main()
