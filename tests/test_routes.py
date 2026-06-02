# ── Integration tests for endpoints ─────────────────────────────────────────
#
# These tests use the 'client' and 'mock_ai' fixtures from conftest.py.
# 'client' is FastAPI's TestClient — it makes real HTTP requests against the API
# without needing a running server. 'mock_ai' ensures OpenAI is not called.


# ── POST /api/suggest ──────────────────────────────────────────────────────────

def test_suggest_returns_200_with_valid_data(client, mock_ai):
    response = client.post("/api/suggest", json={
        "case_description": "EDI 850 PO not being received",
        "investigation_steps": ["Checked cXML logs", "Verified endpoint URL"],
    })

    assert response.status_code == 200
    assert "suggestions" in response.json()
    assert response.json()["suggestions"] == "1. Check the logs\n2. Verify credentials"


def test_suggest_calls_ai_with_correct_context(client, mock_ai):
    client.post("/api/suggest", json={
        "case_description": "Approval workflow stuck",
        "investigation_steps": ["Checked approver config"],
    })

    # Verify generate_suggestions was called (and not skipped)
    assert mock_ai["suggest"].called


def test_suggest_saves_case_to_database(client, mock_ai, memory_db):
    from services.database_service import get_cases

    client.post("/api/suggest", json={
        "case_description": "PO not syncing to ERP",
        "investigation_steps": [],
    })

    cases = get_cases()
    assert len(cases) == 1
    assert cases[0][1] == "PO not syncing to ERP"


def test_suggest_with_empty_description_returns_error(client, mock_ai):
    mock_ai["suggest"].side_effect = ValueError("Empty description")

    response = client.post("/api/suggest", json={
        "case_description": "",
        "investigation_steps": [],
    })

    assert response.status_code == 500


# ── PUT /api/cases/{id} ────────────────────────────────────────────────────────

def test_update_case_returns_200(client, mock_ai, memory_db):
    from services.database_service import save_case, get_cases

    save_case("EDI error", ["Initial step"], "Old response")
    case_id = get_cases()[0][0]

    response = client.put(f"/api/cases/{case_id}", json={
        "case_description": "EDI error",
        "investigation_steps": ["New step", "Initial step"],
    })

    assert response.status_code == 200
    assert "suggestions" in response.json()


# ── POST /api/improve ──────────────────────────────────────────────────────────

def test_improve_returns_enhanced_message(client, mock_ai):
    response = client.post("/api/improve", json={
        "customer_message": "hi we found error pls fix",
        "tone": "empathetic",
        "case_description": "EDI 850 error",
        "investigation_steps": "1. Checked logs",
    })

    assert response.status_code == 200
    assert "improved_message" in response.json()
    assert response.json()["improved_message"] == "Dear customer, we have investigated your issue."


# ── GET /api/cases ─────────────────────────────────────────────────────────────

def test_get_cases_returns_empty_list_initially(client, mock_ai):
    response = client.get("/api/cases")

    assert response.status_code == 200
    assert response.json() == []


def test_get_cases_returns_saved_cases(client, mock_ai):
    client.post("/api/suggest", json={
        "case_description": "Workflow approval stuck",
        "investigation_steps": ["Checked approver", "Verified roles"],
    })

    response = client.get("/api/cases")
    cases = response.json()

    assert len(cases) == 1
    assert cases[0]["case_description"] == "Workflow approval stuck"
    # Steps should come back as a list, not a string
    assert isinstance(cases[0]["investigation_steps"], list)
    assert "Checked approver" in cases[0]["investigation_steps"]


# ── GET /health ────────────────────────────────────────────────────────────────

def test_health_check(client):
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}