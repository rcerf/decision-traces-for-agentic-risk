import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PATH = ROOT / "src" / "merge_signals.py"

spec = importlib.util.spec_from_file_location("merge_signals", PATH)
merge_signals = importlib.util.module_from_spec(spec)
assert spec.loader is not None
sys.path.insert(0, str(PATH.parent))
sys.modules[spec.name] = merge_signals
try:
    spec.loader.exec_module(merge_signals)
finally:
    sys.path.pop(0)


class MergeSignalsTest(unittest.TestCase):
    def test_merge_dedupes_by_url_and_title(self):
        signal = {
            "signal_id": "SIG-ONE",
            "title": "Same",
            "source_url": "https://example.com/a",
            "notes": "first",
        }
        duplicate = dict(signal)
        duplicate["signal_id"] = "SIG-TWO"
        duplicate["notes"] = "second"

        with tempfile.TemporaryDirectory() as tmp:
            one = Path(tmp) / "one.json"
            two = Path(tmp) / "two.json"
            one.write_text(json.dumps([signal]))
            two.write_text(json.dumps([duplicate]))
            merged = merge_signals.merge([one, two])

        self.assertEqual(len(merged), 1)
        self.assertIn("first", merged[0]["notes"])
        self.assertIn("second", merged[0]["notes"])


if __name__ == "__main__":
    unittest.main()
