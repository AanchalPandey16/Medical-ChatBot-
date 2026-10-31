
import sqlite3

DB_NAME = "memory_crud_test.db"


def initialize_db():
    with sqlite3.connect(DB_NAME) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS medical_facts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                category TEXT NOT NULL,
                value TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'approved'
            )
        """)


def add_fact(category, value):
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.execute(
            """
            INSERT INTO medical_facts (category, value)
            VALUES (?, ?)
            """,
            (category, value)
        )
        return cursor.lastrowid


def get_facts():
    with sqlite3.connect(DB_NAME) as conn:
        rows = conn.execute(
            "SELECT id, category, value, status FROM medical_facts"
        ).fetchall()

    return rows


def update_fact(fact_id, new_value):
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.execute(
            "UPDATE medical_facts SET value = ? WHERE id = ?",
            (new_value, fact_id)
        )
        return cursor.rowcount


def delete_fact(fact_id):
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.execute(
            "DELETE FROM medical_facts WHERE id = ?",
            (fact_id,)
        )
        return cursor.rowcount
