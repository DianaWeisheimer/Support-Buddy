import sqlite3

def get_connection():
    conn = sqlite3.connect('cases.db')
    return conn

def create_table():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS cases (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        case_description TEXT,
        investigation_steps TEXT,
        ai_response TEXT
    )
    """)
    conn.commit()
    conn.close()

def save_case(case_description, investigation_steps, ai_response):
    with sqlite3.connect('cases.db') as conn:
        conn.execute("""
            INSERT INTO cases (case_description, investigation_steps, ai_response)
            VALUES (?, ?, ?)
        """, (case_description, investigation_steps, ai_response))
        conn.commit()
    conn.close()

def get_cases():
    with sqlite3.connect('cases.db') as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM cases
            ORDER BY id DESC
        """)
        cases = cursor.fetchall()
    conn.close()
    return cases
