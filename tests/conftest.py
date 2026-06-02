import pytest
import sqlite3
from fastapi.testclient import TestClient
from unittest.mock import patch


@pytest.fixture
def memory_db(monkeypatch):
    import services.database_service as db_module

    conn = sqlite3.connect(":memory:", check_same_thread=False)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS cases (
            id                  INTEGER PRIMARY KEY AUTOINCREMENT,
            case_description    TEXT,
            investigation_steps TEXT,
            ai_response         TEXT
        )
    """)
    conn.commit()

    monkeypatch.setattr(db_module, "get_connection", lambda: conn)
    yield conn
    conn.close()


@pytest.fixture
def mock_ai():
    # api.routes imports functions directly with "from services.ai_service import ...".
    # That creates local copies in the api.routes namespace.
    # Mocking rule: always patch the namespace where the function is USED, not where it is defined.
    with patch("api.routes.generate_suggestions") as mock_suggest, \
         patch("api.routes.improve_message") as mock_improve:

        mock_suggest.return_value = "1. Check the logs\n2. Verify credentials"
        mock_improve.return_value = "Dear customer, we have investigated your issue."

        yield {"suggest": mock_suggest, "improve": mock_improve}


@pytest.fixture
def client(memory_db):
    from api.main import app
    return TestClient(app)