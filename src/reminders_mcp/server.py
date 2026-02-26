"""MCP server exposing macOS Reminders as tools."""

from mcp.server.fastmcp import FastMCP
from reminders_mcp import reminders

mcp = FastMCP("reminders")


@mcp.tool()
def list_reminder_lists() -> list[str]:
    """List all reminder lists available in the macOS Reminders app."""
    return reminders.get_lists()


@mcp.tool()
def list_reminders(list_name: str = "", include_completed: bool = False) -> list[dict]:
    """
    List reminders from the macOS Reminders app.

    Args:
        list_name: Optional name of a specific list to filter by. Leave empty for all lists.
        include_completed: Whether to include completed reminders (default: False).
    """
    return reminders.get_reminders(
        list_name=list_name or None,
        include_completed=include_completed,
    )


@mcp.tool()
def create_reminder(
    name: str,
    list_name: str = "",
    due_date: str = "",
    notes: str = "",
) -> str:
    """
    Create a new reminder in the macOS Reminders app.

    Args:
        name: The title of the reminder.
        list_name: The list to add the reminder to. Uses the default list if empty.
        due_date: Optional due date, e.g. "February 28, 2026 at 9:00 AM".
        notes: Optional notes/body for the reminder.

    Returns:
        The name of the created reminder.
    """
    return reminders.create_reminder(
        name=name,
        list_name=list_name or None,
        due_date=due_date or None,
        notes=notes or None,
    )


@mcp.tool()
def complete_reminder(name: str, list_name: str = "") -> bool:
    """
    Mark a reminder as completed.

    Args:
        name: The exact name of the reminder to complete.
        list_name: Optional list name to narrow the search.

    Returns:
        True if the reminder was found and completed, False otherwise.
    """
    return reminders.complete_reminder(name=name, list_name=list_name or None)


@mcp.tool()
def delete_reminder(name: str, list_name: str = "") -> bool:
    """
    Delete a reminder permanently.

    Args:
        name: The exact name of the reminder to delete.
        list_name: Optional list name to narrow the search.

    Returns:
        True if the reminder was found and deleted, False otherwise.
    """
    return reminders.delete_reminder(name=name, list_name=list_name or None)


def main():
    mcp.run()


if __name__ == "__main__":
    main()
