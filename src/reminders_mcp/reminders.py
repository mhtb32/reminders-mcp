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
                    set rNotes to ""
                    try
                        set rNotes to body of r
                        if rNotes is missing value then
                            set rNotes to ""
                        else
                            set AppleScript's text item delimiters to (ASCII character 10)
                            set noteItems to text items of rNotes
                            set AppleScript's text item delimiters to "⏎"
                            set rNotes to noteItems as string
                            set AppleScript's text item delimiters to ""
                        end if
                    end try
                    set rList to name of l
                    set output to output & rList & "|" & rName & "|" & rCompleted & "|" & rDue & "|" & rNotes & "\\n"
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
        parts = line.split("|", 4)
        if len(parts) >= 3:
            reminders.append({
                "list": parts[0],
                "name": parts[1],
                "completed": parts[2].lower() == "true",
                "due_date": parts[3] if len(parts) > 3 and parts[3] and parts[3] != "missing value" else None,
                "notes": parts[4].replace("⏎", "\n") if len(parts) > 4 and parts[4] else None,
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


def update_reminder(
    name: str,
    list_name: str | None = None,
    new_name: str | None = None,
    notes: str | None = None,
    due_date: str | None = None,
) -> bool:
    """Update properties of an existing reminder. Returns True on success."""
    updates = []
    if new_name is not None:
        updates.append(f'set name of r to "{new_name}"')
    if notes is not None:
        updates.append(f'set body of r to "{notes}"')
    if due_date is not None:
        updates.append(f'set due date of r to date "{due_date}"')

    if not updates:
        return True

    updates_script = "\n                        ".join(updates)

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
                        {updates_script}
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
