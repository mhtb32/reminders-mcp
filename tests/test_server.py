"""Tests for MCP server tool registration."""

from reminders_mcp.server import mcp

EXPECTED_TOOLS = {
    "list_reminder_lists",
    "list_reminders",
    "create_reminder",
    "update_reminder",
    "complete_reminder",
    "delete_reminder",
}


def test_all_tools_registered():
    registered = set(mcp._tool_manager._tools.keys())
    assert EXPECTED_TOOLS == registered


def test_tool_count():
    assert len(mcp._tool_manager._tools) == 6
