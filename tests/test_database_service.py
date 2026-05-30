from services.database_service import save_case, get_cases, update_case, json_to_steps


# ── Testes de json_to_steps ────────────────────────────────────────────────────
#
# Essa função tem lógica de conversão com dois caminhos (JSON novo e texto
# antigo) — é exatamente o tipo de coisa que vale testar unitariamente.
# Não precisa de banco, não precisa de fixture, é pura lógica.

def test_json_to_steps_com_lista_json():
    """Formato novo: JSON com lista de strings."""
    raw = '["Checked logs", "Verified credentials"]'
    result = json_to_steps(raw)
    assert result == ["Checked logs", "Verified credentials"]


def test_json_to_steps_com_texto_puro():
    """Formato antigo: texto separado por linha (retrocompatibilidade)."""
    raw = "Checked logs\nVerified credentials"
    result = json_to_steps(raw)
    assert result == ["Checked logs", "Verified credentials"]


def test_json_to_steps_com_string_vazia():
    """Entrada vazia deve retornar lista vazia, não erro."""
    assert json_to_steps("") == []
    assert json_to_steps("   ") == []


def test_json_to_steps_com_none():
    """None deve retornar lista vazia."""
    assert json_to_steps(None) == []


# ── Testes de save_case e get_cases ───────────────────────────────────────────
#
# Esses testes usam a fixture 'memory_db' do conftest.py.
# Note que o parâmetro da função tem o mesmo nome da fixture —
# é assim que o pytest sabe que deve injetar ela aqui.

def test_save_case_e_recuperar(memory_db):
    """Salvar um case e recuperar deve retornar os dados corretos."""
    steps = ["Checked cXML payload", "Verified EDI mapping"]

    save_case("EDI error on PO confirmation", steps, "Try checking the mapping")

    cases = get_cases()

    assert len(cases) == 1
    assert cases[0][1] == "EDI error on PO confirmation"
    assert cases[0][3] == "Try checking the mapping"


def test_get_cases_retorna_mais_recente_primeiro(memory_db):
    """Cases devem vir em ordem decrescente de ID (mais novo primeiro)."""
    save_case("First case",  ["step 1"], "response 1")
    save_case("Second case", ["step 2"], "response 2")

    cases = get_cases()

    # O mais recente (Second case) deve ser o primeiro da lista
    assert cases[0][1] == "Second case"
    assert cases[1][1] == "First case"


def test_update_case_atualiza_steps_e_resposta(memory_db):
    """Após update, os steps e a resposta devem refletir os novos valores."""
    save_case("EDI error", ["Initial step"], "Initial response")

    cases = get_cases()
    case_id = cases[0][0]

    updated_steps = ["New step added", "Initial step"]
    update_case(case_id, updated_steps, "Updated response")

    cases_after = get_cases()
    assert cases_after[0][3] == "Updated response"