# reminders-mcp

MCP server for macOS Reminders app, written in Python using FastMCP.

## Commands

```bash
uv sync                  # install dependencies
uv run reminders-mcp     # run the server
uv run pytest tests/ -v  # run tests
```

## Architecture

- `src/reminders_mcp/reminders.py` — all macOS Reminders access via AppleScript (`osascript`)
- `src/reminders_mcp/server.py` — MCP tool definitions using FastMCP

## Tools

| Tool | Description |
|------|-------------|
| `list_reminder_lists` | Get all list names |
| `list_reminders` | List reminders with name, due date, notes, completed; optional list filter |
| `create_reminder` | Create with optional due date and notes |
| `update_reminder` | Update title, notes, and/or due date of an existing reminder |
| `complete_reminder` | Mark as completed |
| `delete_reminder` | Delete permanently |

`list_reminders` returns `notes` as a string (multiline notes preserved) or `null`.

## Key Constraints

- **macOS only** — everything goes through AppleScript; no cross-platform support
- **Sections not supported** — macOS Reminders sections are not exposed via AppleScript or EventKit's public API
- **No direct DB access** — the Reminders SQLite store is behind sandbox restrictions

## Testing

Tests mock `subprocess.run` to avoid needing the Reminders app or macOS. All AppleScript calls go through `_run_applescript()` in `reminders.py`, which is the right place to patch.

```python
with patch("subprocess.run", return_value=mock_run("ok")):
    ...
```

CI runs on `macos-latest` via GitHub Actions on every push and PR to `main`.

## Dependency Management

Uses `uv`. Do not use `pip` directly. To add a package: `uv add <package>`. Dev dependencies: `uv add --dev <package>`.

## Claude Desktop Config

Server is registered in `~/Library/Application Support/Claude/claude_desktop_config.json` under the key `🖊️ reminders`.
