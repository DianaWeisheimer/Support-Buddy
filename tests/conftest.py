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
    # O routes.py importa as funções diretamente com "from services.ai_service import ...".
    # Isso cria cópias locais no namespace de api.routes.
    # Regra do mock: sempre mockar no namespace onde a função É USADA, não onde foi definida.
    with patch("api.routes.generate_suggestions") as mock_suggest, \
         patch("api.routes.improve_message") as mock_improve:

        mock_suggest.return_value = "1. Check the logs\n2. Verify credentials"
        mock_improve.return_value = "Dear customer, we have investigated your issue."

        yield {"suggest": mock_suggest, "improve": mock_improve}


@pytest.fixture
def client(memory_db):
    from api.main import app
    return TestClient(app)