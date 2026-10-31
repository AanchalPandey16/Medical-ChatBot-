
import sqlite3

DB_NAME = "memory_chat_test.db"

ALLOWED_CATEGORIES = {
    "allergies",
    "medications",
    "current_symptoms",
    "confirmed_conditions",
    "unconfirmed_conditions"
}


def get_connection():
    return sqlite3.connect(DB_NAME)


# Create database table
def initialize_db():

    with get_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS medical_facts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                chat_id INTEGER NOT NULL,
                category TEXT NOT NULL,
                value TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'approved',
                UNIQUE(chat_id, category, value)
            )
        """)


# CREATE
def add_fact(chat_id, category, value):

    if type(chat_id) is not int or chat_id <= 0:
        raise ValueError("Invalid chat ID")

    if category not in ALLOWED_CATEGORIES:
        raise ValueError("Invalid category")

    if not isinstance(value, str) or not value.strip():
        raise ValueError("Invalid fact value")

    with get_connection() as conn:

        cursor = conn.execute("""
            INSERT OR IGNORE INTO medical_facts
            (chat_id, category, value)
            VALUES (?, ?, ?)
        """, (chat_id, category, value.strip()))

        return cursor.rowcount


# READ
def get_facts(chat_id):

    with get_connection() as conn:

        rows = conn.execute("""
            SELECT id, category, value, status
            FROM medical_facts
            WHERE chat_id = ?
            ORDER BY id
        """, (chat_id,)).fetchall()

    return rows


# UPDATE
def update_fact(chat_id, fact_id, new_value):

    if not isinstance(new_value, str) or not new_value.strip():
        raise ValueError("Invalid fact value")

    with get_connection() as conn:

        cursor = conn.execute("""
            UPDATE medical_facts
            SET value = ?
            WHERE id = ? AND chat_id = ?
        """, (new_value.strip(), fact_id, chat_id))

        return cursor.rowcount


# DELETE
def delete_fact(chat_id, fact_id):

    with get_connection() as conn:

        cursor = conn.execute("""
            DELETE FROM medical_facts
            WHERE id = ? AND chat_id = ?
        """, (fact_id, chat_id))

        return cursor.rowcount
