import json
import sqlite3


def get_connection():
    return sqlite3.connect("cases.db")


def create_table():
    with get_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS cases (
                id                  INTEGER PRIMARY KEY AUTOINCREMENT,
                case_description    TEXT,
                investigation_steps TEXT,
                ai_response         TEXT
            )
        """)
        conn.commit()


def steps_to_json(steps: list[str]) -> str:
    """Converte lista de steps para string JSON para salvar no banco."""
    return json.dumps(steps, ensure_ascii=False)


def json_to_steps(raw: str) -> list[str]:
    """
    Converte string do banco de volta para lista.
    Suporta o formato antigo (texto puro) e o novo (JSON).
    """
    if not raw or not raw.strip():
        return []
    try:
        parsed = json.loads(raw)
        if isinstance(parsed, list):
            return parsed
        # Era um JSON mas não era lista — trata como texto
        return [raw]
    except (json.JSONDecodeError, ValueError):
        # Formato antigo: texto puro separado por linha
        return [line.strip() for line in raw.strip().splitlines() if line.strip()]


def save_case(case_description: str, steps: list[str], ai_response: str):
    with get_connection() as conn:
        conn.execute(
            """
            INSERT INTO cases (case_description, investigation_steps, ai_response)
            VALUES (?, ?, ?)
            """,
            (case_description, steps_to_json(steps), ai_response),
        )
        conn.commit()


def update_case(case_id: int, steps: list[str], ai_response: str):
    with get_connection() as conn:
        conn.execute(
            """
            UPDATE cases
            SET investigation_steps = ?, ai_response = ?
            WHERE id = ?
            """,
            (steps_to_json(steps), ai_response, case_id),
        )
        conn.commit()


def get_cases() -> list[tuple]:
    with get_connection() as conn:
        cursor = conn.execute("SELECT * FROM cases ORDER BY id DESC")
        return cursor.fetchall()
