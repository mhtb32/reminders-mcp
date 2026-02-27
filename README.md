# 🖊️ reminders-mcp

![reminders-mcp](assets/readme-image.png)

> **macOS only** — this server uses AppleScript to communicate with the macOS Reminders app.

A [Model Context Protocol (MCP)](https://modelcontextprotocol.io) server that lets Claude read and manage your macOS Reminders. Create, list, update, complete, and delete reminders directly from any MCP-compatible client such as Claude Desktop.

## Requirements

- macOS
- Python 3.11+
- [uv](https://docs.astral.sh/uv/) — install with `curl -LsSf https://astral.sh/uv/install.sh | sh`
- macOS Reminders app (you'll be prompted to grant Automation permission on first run)

## Installation

```bash
git clone https://github.com/mhtb32/reminders-mcp.git
cd reminders-mcp
uv sync
```

## Claude Desktop Setup

Add the following to `~/Library/Application Support/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "🖊️ reminders": {
      "command": "/Users/YOUR_USERNAME/.local/bin/uv",
      "args": ["run", "--directory", "/path/to/reminders-mcp", "reminders-mcp"]
    }
  }
}
```

Replace `YOUR_USERNAME` and `/path/to/reminders-mcp` with your actual values, then restart Claude Desktop.

## Tools

| Tool | Description |
|------|-------------|
| `list_reminder_lists` | Get all reminder list names |
| `list_reminders` | List reminders (with name, due date, notes, and completion status), optionally filtered by list |
| `create_reminder` | Create a reminder with optional due date and notes |
| `update_reminder` | Update the title, notes, or due date of an existing reminder |
| `complete_reminder` | Mark a reminder as completed |
| `delete_reminder` | Delete a reminder permanently |

## Example Usage

Once connected, you can ask Claude things like:

- _"What are my reminders for today?"_
- _"Add a reminder to buy groceries tomorrow at 9am"_
- _"Update the notes on my 'Call dentist' reminder to include the phone number"_
- _"Rename my 'Pay rent' reminder to 'Pay rent + utilities'"_
- _"Mark the 'Call dentist' reminder as done"_
- _"Show me everything in my Work list"_

## How It Works

This server uses **AppleScript** to communicate with the macOS Reminders app. No data leaves your machine — everything runs locally.

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

## License

MIT
