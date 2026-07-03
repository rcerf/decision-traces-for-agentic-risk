import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[spec.name] = module
    sys.path.insert(0, str(path.parent))
    try:
        spec.loader.exec_module(module)
    finally:
        sys.path.pop(0)
    return module


ingest_arxiv = load_module("ingest_arxiv", ROOT / "src" / "ingest_arxiv.py")
ingest_aiid = load_module("ingest_aiid", ROOT / "src" / "ingest_aiid.py")
ingest_manual_social = load_module("ingest_manual_social", ROOT / "src" / "ingest_manual_social.py")
signal_triage = load_module("signal_triage_for_ingest_tests", ROOT / "src" / "signal_triage.py")


ARXIV_SAMPLE = """<?xml version='1.0' encoding='UTF-8'?>
<feed xmlns="http://www.w3.org/2005/Atom">
  <entry>
    <id>http://arxiv.org/abs/2601.00001v1</id>
    <updated>2026-01-02T00:00:00Z</updated>
    <published>2026-01-01T00:00:00Z</published>
    <title>Prompt Injection Guards for Tool-Using Agents</title>
    <summary>We study indirect prompt injection in tool-using LLM agents.</summary>
    <link href="https://arxiv.org/abs/2601.00001" rel="alternate" type="text/html"/>
  </entry>
</feed>
"""


class IngestionAdapterTest(unittest.TestCase):
    def test_arxiv_feed_becomes_valid_source_signal(self):
        records = ingest_arxiv.parse_feed(ARXIV_SAMPLE)
        signals = ingest_arxiv.query_to_signals(
            {
                "name": "test-query",
                "query": "all:test",
                "affected_surfaces": ["ingress", "tool_calling"],
                "risk_categories": ["prompt_injection"],
                "proposed_probe_stage": "ingress",
            },
            records,
        )

        self.assertEqual(len(signals), 1)
        self.assertEqual(signal_triage.validate_signal(signals[0]), [])
        self.assertEqual(signals[0]["source_type"], "research")

    def test_aiid_snapshot_becomes_valid_source_signal(self):
        signals = ingest_aiid.snapshot_to_signals(
            [
                {
                    "incident_id": "123",
                    "title": "Synthetic incident summary",
                    "summary": "A public AI incident created financial harm.",
                    "url": "https://example.com/incident",
                    "date": "2026-01-01",
                }
            ]
        )

        self.assertEqual(len(signals), 1)
        self.assertEqual(signal_triage.validate_signal(signals[0]), [])
        self.assertEqual(signals[0]["source_type"], "incident_database")

    def test_manual_social_defaults_to_review_gated_no_raw_reproduction(self):
        record = {
            "title": "Wrapper jailbreak motif",
            "source_url": "https://example.com/post",
            "summary": "Safe abstraction only.",
        }
        signal = ingest_manual_social.normalize_record(record)

        self.assertEqual(signal_triage.validate_signal(signal), [])
        self.assertEqual(signal["source_tier"], 3)
        self.assertEqual(signal["raw_detail_policy"], "do_not_reproduce")

    def test_manual_social_csv_loads(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "social.csv"
            path.write_text(
                "title,source_url,summary,risk_categories,affected_surfaces\n"
                "Test motif,https://example.com,Safe summary,jailbreak_motif,ingress\n"
            )
            records = ingest_manual_social.load_records(str(path))

        self.assertEqual(len(records), 1)
        self.assertEqual(records[0]["title"], "Test motif")


if __name__ == "__main__":
    unittest.main()
