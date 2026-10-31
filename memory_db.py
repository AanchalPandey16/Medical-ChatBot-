
import sqlite3
import json

DB_NAME = "memory_test.db"


def initialize_memory_db():
    with sqlite3.connect(DB_NAME) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS approved_context (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                context_data TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)


def save_approved_context(context):
    with sqlite3.connect(DB_NAME) as conn:
        conn.execute(
            """
            INSERT INTO approved_context (context_data)
            VALUES (?)
            """,
            (json.dumps(context),)
        )


def get_approved_context():
    with sqlite3.connect(DB_NAME) as conn:
        rows = conn.execute(
            "SELECT id, context_data FROM approved_context"
        ).fetchall()

    return [
        {
            "id": row[0],
            "context": json.loads(row[1])
        }
        for row in rows
    ]
