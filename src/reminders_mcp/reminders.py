"""macOS Reminders interface via AppleScript."""

import subprocess
from datetime import datetime


def _run_applescript(script: str) -> str:
    result = subprocess.run(
        ["osascript", "-e", script],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise RuntimeError(f"AppleScript error: {result.stderr.strip()}")
    return result.stdout.strip()


def get_lists() -> list[str]:
    """Return all reminder list names."""
    script = """
        tell application "Reminders"
            set listNames to {}
            repeat with l in lists
                set end of listNames to name of l
            end repeat
            return listNames
        end tell
    """
    output = _run_applescript(script)
    if not output:
        return []
    return [name.strip() for name in output.split(",")]


def get_reminders(list_name: str | None = None, include_completed: bool = False) -> list[dict]:
    """Return reminders, optionally filtered by list."""
    if list_name:
        target = f'list "{list_name}"'
    else:
        target = "lists"

    completed_filter = "" if include_completed else "whose completed is false"

    script = f"""
        tell application "Reminders"
            set output to ""
            if "{list_name or ""}" is not "" then
                set theList to {{list "{list_name or ""}"}}
            else
                set theList to lists
            end if
            repeat with l in theList
                repeat with r in (reminders of l {completed_filter})
                    set rName to name of r
                    set rCompleted to completed of r as string
                    set rDue to ""
                    try
                        set rDue to due date of r as string
                    end try
                    set rList to name of l
                    set output to output & rList & "|" & rName & "|" & rCompleted & "|" & rDue & "\\n"
                end repeat
            end repeat
            return output
        end tell
    """
    output = _run_applescript(script)
    reminders = []
    for line in output.splitlines():
        line = line.strip()
        if not line:
            continue
        parts = line.split("|")
        if len(parts) >= 3:
            reminders.append({
                "list": parts[0],
                "name": parts[1],
                "completed": parts[2].lower() == "true",
                "due_date": parts[3] if len(parts) > 3 and parts[3] and parts[3] != "missing value" else None,
            })
    return reminders


def create_reminder(name: str, list_name: str | None = None, due_date: str | None = None, notes: str | None = None) -> str:
    """Create a new reminder. Returns the reminder name."""
    props = [f'name:"{name}"']
    if due_date:
        props.append(f'due date:date "{due_date}"')
    if notes:
        props.append(f'body:"{notes}"')
    props_str = ", ".join(props)

    if list_name:
        target = f'list "{list_name}"'
    else:
        target = "default list"

    script = f"""
        tell application "Reminders"
            set newReminder to make new reminder at end of {target} with properties {{{props_str}}}
            return name of newReminder
        end tell
    """
    return _run_applescript(script)


def complete_reminder(name: str, list_name: str | None = None) -> bool:
    """Mark a reminder as completed. Returns True on success."""
    if list_name:
        target = f'list "{list_name}"'
    else:
        target = "lists"

    script = f"""
        tell application "Reminders"
            if "{list_name or ""}" is not "" then
                set theList to {{list "{list_name or ""}"}}
            else
                set theList to lists
            end if
            repeat with l in theList
                repeat with r in reminders of l
                    if name of r is "{name}" then
                        set completed of r to true
                        return "ok"
                    end if
                end repeat
            end repeat
            return "not found"
        end tell
    """
    result = _run_applescript(script)
    return result == "ok"


def delete_reminder(name: str, list_name: str | None = None) -> bool:
    """Delete a reminder. Returns True on success."""
    if list_name:
        script = f"""
            tell application "Reminders"
                set matches to (reminders of list "{list_name}" whose name is "{name}")
                if length of matches > 0 then
                    delete item 1 of matches
                    return "ok"
                end if
                return "not found"
            end tell
        """
    else:
        script = f"""
            tell application "Reminders"
                repeat with l in lists
                    set matches to (reminders of l whose name is "{name}")
                    if length of matches > 0 then
                        delete item 1 of matches
                        return "ok"
                    end if
                end repeat
                return "not found"
            end tell
        """
    result = _run_applescript(script)
    return result == "ok"
