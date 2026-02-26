# reminders-mcp

A [Model Context Protocol (MCP)](https://modelcontextprotocol.io) server that exposes the macOS Reminders app as tools for Claude.

## Requirements

- macOS
- Python 3.11+
- [uv](https://docs.astral.sh/uv/)
- macOS Reminders app (grant Automation permission when prompted)

## Setup

```bash
# Install dependencies
uv sync

# Run the server directly (for testing)
uv run reminders-mcp
```

## Tools

| Tool | Description |
|------|-------------|
| `list_reminder_lists` | Get all reminder list names |
| `list_reminders` | List reminders, optionally filtered by list and completion status |
| `create_reminder` | Create a reminder with optional due date and notes |
| `complete_reminder` | Mark a reminder as completed |
| `delete_reminder` | Delete a reminder permanently |

## Connect to Claude Desktop

Merge the following into `~/Library/Application Support/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "reminders": {
      "command": "/Users/nobitex/.local/bin/uv",
      "args": ["run", "--directory", "/Users/nobitex/Projects/reminders-mcp", "reminders-mcp"]
    }
  }
}
```

Then restart Claude Desktop. Claude will have access to all five tools above.

## Project Structure

```
reminders-mcp/
├── src/reminders_mcp/
│   ├── __init__.py
│   ├── reminders.py   # AppleScript interface to macOS Reminders
│   └── server.py      # MCP server (FastMCP)
├── pyproject.toml
├── uv.lock
└── README.md
```
