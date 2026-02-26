"""Unit tests for reminders.py — AppleScript calls are fully mocked."""

from unittest.mock import MagicMock, patch

import pytest

from reminders_mcp.reminders import (
    complete_reminder,
    create_reminder,
    delete_reminder,
    get_lists,
    get_reminders,
)


def mock_run(stdout="", returncode=0):
    """Helper to build a mock subprocess.run result."""
    result = MagicMock()
    result.stdout = stdout
    result.stderr = ""
    result.returncode = returncode
    return result


# ---------------------------------------------------------------------------
# get_lists
# ---------------------------------------------------------------------------

class TestGetLists:
    def test_returns_list_of_names(self):
        with patch("subprocess.run", return_value=mock_run("Work, Personal, Groceries")):
            assert get_lists() == ["Work", "Personal", "Groceries"]

    def test_single_list(self):
        with patch("subprocess.run", return_value=mock_run("Inbox")):
            assert get_lists() == ["Inbox"]

    def test_empty_output_returns_empty_list(self):
        with patch("subprocess.run", return_value=mock_run("")):
            assert get_lists() == []

    def test_applescript_error_raises(self):
        with patch("subprocess.run", return_value=mock_run(returncode=1)):
            with pytest.raises(RuntimeError, match="AppleScript error"):
                get_lists()


# ---------------------------------------------------------------------------
# get_reminders
# ---------------------------------------------------------------------------

class TestGetReminders:
    def test_parses_basic_reminder(self):
        output = "Work|Buy coffee|false|missing value\n"
        with patch("subprocess.run", return_value=mock_run(output)):
            result = get_reminders()
        assert len(result) == 1
        assert result[0] == {
            "list": "Work",
            "name": "Buy coffee",
            "completed": False,
            "due_date": None,
        }

    def test_missing_value_due_date_becomes_none(self):
        output = "Personal|Call dentist|false|missing value\n"
        with patch("subprocess.run", return_value=mock_run(output)):
            result = get_reminders()
        assert result[0]["due_date"] is None

    def test_real_due_date_is_preserved(self):
        output = "Work|Submit report|false|Thursday, February 27, 2026 at 9:00 AM\n"
        with patch("subprocess.run", return_value=mock_run(output)):
            result = get_reminders()
        assert result[0]["due_date"] == "Thursday, February 27, 2026 at 9:00 AM"

    def test_completed_flag_parsed_correctly(self):
        output = "Work|Done task|true|missing value\n"
        with patch("subprocess.run", return_value=mock_run(output)):
            result = get_reminders()
        assert result[0]["completed"] is True

    def test_multiple_reminders(self):
        output = "Work|Task A|false|missing value\nWork|Task B|true|missing value\n"
        with patch("subprocess.run", return_value=mock_run(output)):
            result = get_reminders()
        assert len(result) == 2
        assert result[0]["name"] == "Task A"
        assert result[1]["name"] == "Task B"

    def test_empty_output_returns_empty_list(self):
        with patch("subprocess.run", return_value=mock_run("")):
            assert get_reminders() == []

    def test_malformed_lines_are_skipped(self):
        output = "OnlyOneField\nWork|Task|false|missing value\n"
        with patch("subprocess.run", return_value=mock_run(output)):
            result = get_reminders()
        assert len(result) == 1
        assert result[0]["name"] == "Task"


# ---------------------------------------------------------------------------
# create_reminder
# ---------------------------------------------------------------------------

class TestCreateReminder:
    def test_returns_reminder_name(self):
        with patch("subprocess.run", return_value=mock_run("Buy milk")):
            result = create_reminder("Buy milk")
        assert result == "Buy milk"

    def test_with_list_name(self):
        with patch("subprocess.run", return_value=mock_run("Buy milk")) as mock:
            create_reminder("Buy milk", list_name="Groceries")
            script = mock.call_args[0][0][2]
            assert 'list "Groceries"' in script

    def test_with_due_date(self):
        with patch("subprocess.run", return_value=mock_run("Pay rent")) as mock:
            create_reminder("Pay rent", due_date="March 1, 2026 at 9:00 AM")
            script = mock.call_args[0][0][2]
            assert "due date" in script

    def test_with_notes(self):
        with patch("subprocess.run", return_value=mock_run("Task")) as mock:
            create_reminder("Task", notes="Some note")
            script = mock.call_args[0][0][2]
            assert "body" in script

    def test_uses_default_list_when_no_list_name(self):
        with patch("subprocess.run", return_value=mock_run("Task")) as mock:
            create_reminder("Task")
            script = mock.call_args[0][0][2]
            assert "default list" in script

    def test_applescript_error_raises(self):
        with patch("subprocess.run", return_value=mock_run(returncode=1)):
            with pytest.raises(RuntimeError):
                create_reminder("Task")


# ---------------------------------------------------------------------------
# complete_reminder
# ---------------------------------------------------------------------------

class TestCompleteReminder:
    def test_returns_true_on_success(self):
        with patch("subprocess.run", return_value=mock_run("ok")):
            assert complete_reminder("Buy milk") is True

    def test_returns_false_when_not_found(self):
        with patch("subprocess.run", return_value=mock_run("not found")):
            assert complete_reminder("Nonexistent") is False

    def test_with_list_name_scopes_search(self):
        with patch("subprocess.run", return_value=mock_run("ok")) as mock:
            complete_reminder("Buy milk", list_name="Groceries")
            script = mock.call_args[0][0][2]
            assert "Groceries" in script

    def test_applescript_error_raises(self):
        with patch("subprocess.run", return_value=mock_run(returncode=1)):
            with pytest.raises(RuntimeError):
                complete_reminder("Task")


# ---------------------------------------------------------------------------
# delete_reminder
# ---------------------------------------------------------------------------

class TestDeleteReminder:
    def test_returns_true_on_success(self):
        with patch("subprocess.run", return_value=mock_run("ok")):
            assert delete_reminder("Buy milk") is True

    def test_returns_false_when_not_found(self):
        with patch("subprocess.run", return_value=mock_run("not found")):
            assert delete_reminder("Nonexistent") is False

    def test_with_list_name_uses_whose_filter(self):
        with patch("subprocess.run", return_value=mock_run("ok")) as mock:
            delete_reminder("Buy milk", list_name="Groceries")
            script = mock.call_args[0][0][2]
            assert 'list "Groceries"' in script
            assert "whose name is" in script

    def test_without_list_name_searches_all_lists(self):
        with patch("subprocess.run", return_value=mock_run("ok")) as mock:
            delete_reminder("Buy milk")
            script = mock.call_args[0][0][2]
            assert "repeat with l in lists" in script

    def test_applescript_error_raises(self):
        with patch("subprocess.run", return_value=mock_run(returncode=1)):
            with pytest.raises(RuntimeError):
                delete_reminder("Task")
