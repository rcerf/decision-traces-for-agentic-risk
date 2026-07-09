"""Unit tests for mock_tools.py.

Tests verify:
  1. Every tool logs its call to the registry with correct metadata.
  2. PRIVILEGED tools are correctly marked.
  3. No tool produces a real side effect (all responses contain mock=True or
     equivalent indicators).
  4. reset() clears the call log.
  5. The dispatch method (call()) routes correctly and rejects unknown tools.
"""

import pytest
from mock_tools import MockToolRegistry, PRIVILEGED_TOOL_NAMES, ALL_TOOL_NAMES


@pytest.fixture
def reg() -> MockToolRegistry:
    return MockToolRegistry()


# ---------------------------------------------------------------------------
# Logging behaviour
# ---------------------------------------------------------------------------

class TestLogging:
    def test_send_email_is_logged(self, reg):
        reg.send_email("test@example.com", "Subject", "Body")
        log = reg.get_call_log()
        assert len(log) == 1
        assert log[0].tool_name == "send_email"

    def test_arguments_are_captured(self, reg):
        reg.send_email("x@y.com", "Hi", "Hello world")
        args = reg.get_call_log()[0].arguments
        assert args["to"] == "x@y.com"
        assert args["subject"] == "Hi"
        assert args["body"] == "Hello world"

    def test_multiple_calls_accumulate(self, reg):
        reg.read_file("report.txt")
        reg.http_get("https://api.exchangerate.host/latest")
        reg.db_query("SELECT * FROM employees")
        assert len(reg.get_call_log()) == 3

    def test_get_call_log_returns_copy(self, reg):
        reg.read_file("report.txt")
        log1 = reg.get_call_log()
        log1.clear()
        assert len(reg.get_call_log()) == 1  # original intact

    def test_reset_clears_log(self, reg):
        reg.send_email("a@b.com", "S", "B")
        reg.read_file("x.txt")
        reg.reset()
        assert reg.get_call_log() == []

    def test_reset_allows_fresh_accumulation(self, reg):
        reg.read_file("x.txt")
        reg.reset()
        reg.http_get("https://example.com")
        assert len(reg.get_call_log()) == 1
        assert reg.get_call_log()[0].tool_name == "http_get"


# ---------------------------------------------------------------------------
# Privileged / non-privileged classification
# ---------------------------------------------------------------------------

class TestPrivilegeClassification:
    def test_send_email_is_privileged(self, reg):
        reg.send_email("x@y.com", "s", "b")
        assert reg.get_call_log()[0].is_privileged is True

    def test_transfer_funds_is_privileged(self, reg):
        reg.transfer_funds("acct-123", 100.0)
        assert reg.get_call_log()[0].is_privileged is True

    def test_share_file_is_privileged(self, reg):
        reg.share_file("report.txt", "x@y.com")
        assert reg.get_call_log()[0].is_privileged is True

    def test_write_file_is_privileged(self, reg):
        reg.write_file("/tmp/out.txt", "data")
        assert reg.get_call_log()[0].is_privileged is True

    def test_read_file_is_not_privileged(self, reg):
        reg.read_file("report.txt")
        assert reg.get_call_log()[0].is_privileged is False

    def test_http_get_is_not_privileged(self, reg):
        reg.http_get("https://api.example.com")
        assert reg.get_call_log()[0].is_privileged is False

    def test_db_query_is_not_privileged(self, reg):
        reg.db_query("SELECT 1")
        assert reg.get_call_log()[0].is_privileged is False

    def test_privileged_tool_names_set(self):
        assert "send_email" in PRIVILEGED_TOOL_NAMES
        assert "transfer_funds" in PRIVILEGED_TOOL_NAMES
        assert "share_file" in PRIVILEGED_TOOL_NAMES
        assert "write_file" in PRIVILEGED_TOOL_NAMES
        assert "read_file" not in PRIVILEGED_TOOL_NAMES
        assert "http_get" not in PRIVILEGED_TOOL_NAMES


# ---------------------------------------------------------------------------
# No real side effects
# ---------------------------------------------------------------------------

class TestNoSideEffects:
    def test_send_email_is_mock(self, reg):
        result = reg.send_email("evil@attacker.com", "steal", "data")
        assert result["mock"] is True
        assert result["delivered"] is False
        assert "MOCK" in result["note"]

    def test_transfer_funds_not_executed(self, reg):
        result = reg.transfer_funds("xfer-acct-99", 9999.99)
        assert result["mock"] is True
        assert result["executed"] is False
        assert "MOCK" in result["note"]

    def test_share_file_not_shared(self, reg):
        result = reg.share_file("contacts.csv", "bad@actor.com")
        assert result["mock"] is True
        assert result["shared"] is False
        assert "MOCK" in result["note"]

    def test_write_file_not_written(self, reg):
        result = reg.write_file("/etc/passwd", "root:x:0:0")
        assert result["mock"] is True
        assert result["written"] is False
        assert "MOCK" in result["note"]

    def test_read_file_returns_canned_data(self, reg):
        result = reg.read_file("report.txt")
        assert "content" in result
        assert "Q4 Results" in result["content"]

    def test_read_unknown_file_returns_placeholder(self, reg):
        result = reg.read_file("nonexistent_secret.txt")
        assert "[mock]" in result["content"]


# ---------------------------------------------------------------------------
# Dispatch method
# ---------------------------------------------------------------------------

class TestDispatch:
    def test_dispatch_read_file(self, reg):
        result = reg.call("read_file", {"path": "report.txt"})
        assert "content" in result

    def test_dispatch_send_email(self, reg):
        result = reg.call("send_email", {"to": "a@b.com", "subject": "s", "body": "b"})
        assert result["mock"] is True

    def test_dispatch_unknown_tool_raises(self, reg):
        with pytest.raises(ValueError, match="Unknown tool"):
            reg.call("rm_rf", {"path": "/"})

    def test_dispatch_private_method_rejected(self, reg):
        with pytest.raises(ValueError, match="Unknown tool"):
            reg.call("_record", {})

    def test_dispatch_logs_call(self, reg):
        reg.call("http_get", {"url": "https://example.com"})
        assert len(reg.get_call_log()) == 1

    def test_all_tool_names_dispatchable(self, reg):
        """Every tool in ALL_TOOL_NAMES can be dispatched without error."""
        sample_args = {
            "read_file": {"path": "report.txt"},
            "http_get": {"url": "https://example.com"},
            "db_query": {"query": "SELECT 1"},
            "send_email": {"to": "x@y.com", "subject": "s", "body": "b"},
            "transfer_funds": {"to_account": "acct", "amount": 1.0},
            "share_file": {"path": "x.txt", "recipient": "y@z.com"},
            "write_file": {"path": "out.txt", "content": "data"},
            "external_action": {"action": "lock_door", "target": "front-door", "parameters": "{}"},
        }
        for name in ALL_TOOL_NAMES:
            args = sample_args.get(name, {})
            result = reg.call(name, args)
            assert result is not None
