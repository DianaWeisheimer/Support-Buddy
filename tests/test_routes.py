# ── Testes de integração dos endpoints ────────────────────────────────────────
#
# Esses testes usam as fixtures 'client' e 'mock_ai' do conftest.py.
# 'client' é o TestClient da FastAPI — faz requests HTTP reais contra a API
# sem precisar de servidor. 'mock_ai' garante que a OpenAI não é chamada.


# ── POST /api/suggest ──────────────────────────────────────────────────────────

def test_suggest_retorna_200_com_dados_validos(client, mock_ai):
    """Endpoint deve retornar 200 e o campo 'suggestions' preenchido."""
    response = client.post("/api/suggest", json={
        "case_description": "EDI 850 PO not being received",
        "investigation_steps": ["Checked cXML logs", "Verified endpoint URL"],
    })

    assert response.status_code == 200
    assert "suggestions" in response.json()
    assert response.json()["suggestions"] == "1. Check the logs\n2. Verify credentials"


def test_suggest_chama_ai_com_contexto_correto(client, mock_ai):
    """A IA deve ser chamada com a descrição do case."""
    client.post("/api/suggest", json={
        "case_description": "Approval workflow stuck",
        "investigation_steps": ["Checked approver config"],
    })

    # Verifica se generate_suggestions foi chamada (e não pulada)
    assert mock_ai["suggest"].called


def test_suggest_salva_case_no_banco(client, mock_ai, memory_db):
    """Após o POST, o case deve estar salvo no banco."""
    from services.database_service import get_cases

    client.post("/api/suggest", json={
        "case_description": "PO not syncing to ERP",
        "investigation_steps": [],
    })

    cases = get_cases()
    assert len(cases) == 1
    assert cases[0][1] == "PO not syncing to ERP"


def test_suggest_com_descricao_vazia_retorna_erro(client, mock_ai):
    """
    Descrição vazia deve retornar erro 500 pois a IA vai falhar
    sem contexto. Pydantic valida o tipo, mas a lógica de negócio
    rejeita strings vazias.
    """
    # Força a IA a lançar um erro com input vazio
    mock_ai["suggest"].side_effect = ValueError("Empty description")

    response = client.post("/api/suggest", json={
        "case_description": "",
        "investigation_steps": [],
    })

    assert response.status_code == 500


# ── PUT /api/cases/{id} ────────────────────────────────────────────────────────

def test_update_case_retorna_200(client, mock_ai, memory_db):
    """Atualizar um case existente deve retornar 200 com novas sugestões."""
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

def test_improve_retorna_mensagem_melhorada(client, mock_ai):
    """Endpoint deve retornar 200 e o campo 'improved_message'."""
    response = client.post("/api/improve", json={
        "customer_message": "hi we found error pls fix",
        "case_description": "EDI 850 error",
        "investigation_steps": "1. Checked logs",
    })

    assert response.status_code == 200
    assert "improved_message" in response.json()
    assert response.json()["improved_message"] == "Dear customer, we have investigated your issue."


# ── GET /api/cases ─────────────────────────────────────────────────────────────

def test_get_cases_retorna_lista_vazia_inicialmente(client, mock_ai):
    """Sem cases salvos, deve retornar lista vazia (não erro)."""
    response = client.get("/api/cases")

    assert response.status_code == 200
    assert response.json() == []


def test_get_cases_retorna_cases_salvos(client, mock_ai):
    """Após salvar, GET /cases deve retornar os dados com steps como lista."""
    client.post("/api/suggest", json={
        "case_description": "Workflow approval stuck",
        "investigation_steps": ["Checked approver", "Verified roles"],
    })

    response = client.get("/api/cases")
    cases = response.json()

    assert len(cases) == 1
    assert cases[0]["case_description"] == "Workflow approval stuck"
    # Steps devem vir como lista, não como string
    assert isinstance(cases[0]["investigation_steps"], list)
    assert "Checked approver" in cases[0]["investigation_steps"]


# ── GET /health ────────────────────────────────────────────────────────────────

def test_health_check(client):
    """Health endpoint deve sempre retornar 200 com status ok."""
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}