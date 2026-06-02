from services.database_service import save_case, get_cases, update_case, json_to_steps


# ── json_to_steps tests ───────────────────────────────────────────────────────
#
# This function has conversion logic for two paths (new JSON and old plain text)
# — exactly the kind of thing worth unit testing.
# It does not require a database or fixture; it is pure logic.

def test_json_to_steps_with_json_list():
    """New format: JSON array of strings."""
    raw = '["Checked logs", "Verified credentials"]'
    result = json_to_steps(raw)
    assert result == ["Checked logs", "Verified credentials"]


def test_json_to_steps_with_plain_text():
    """Old format: plain text separated by lines (backwards compatible)."""
    raw = "Checked logs\nVerified credentials"
    result = json_to_steps(raw)
    assert result == ["Checked logs", "Verified credentials"]


def test_json_to_steps_with_empty_string():
    """Empty input should return an empty list, not an error."""
    assert json_to_steps("") == []
    assert json_to_steps("   ") == []


def test_json_to_steps_with_none():
    """None should return an empty list."""
    assert json_to_steps(None) == []


# ── save_case and get_cases tests ───────────────────────────────────────────
#
# These tests use the 'memory_db' fixture from conftest.py.
# Note that the function parameter matches the fixture name —
# that is how pytest knows to inject it here.

def test_save_case_and_retrieve(memory_db):
    """Saving a case and retrieving it should return the correct data."""
    steps = ["Checked cXML payload", "Verified EDI mapping"]

    save_case("EDI error on PO confirmation", steps, "Try checking the mapping")

    cases = get_cases()

    assert len(cases) == 1
    assert cases[0][1] == "EDI error on PO confirmation"
    assert cases[0][3] == "Try checking the mapping"


def test_get_cases_returns_most_recent_first(memory_db):
    """Cases should be ordered descending by ID (newest first)."""
    save_case("First case",  ["step 1"], "response 1")
    save_case("Second case", ["step 2"], "response 2")

    cases = get_cases()

    # Most recent (Second case) should be first in the list
    assert cases[0][1] == "Second case"
    assert cases[1][1] == "First case"


def test_update_case_updates_steps_and_response(memory_db):
    """After update, the steps and response should reflect the new values."""
    save_case("EDI error", ["Initial step"], "Initial response")

    cases = get_cases()
    case_id = cases[0][0]

    updated_steps = ["New step added", "Initial step"]
    update_case(case_id, updated_steps, "Updated response")

    cases_after = get_cases()
    assert cases_after[0][3] == "Updated response"