import os
from contextlib import contextmanager
from typing import Any

import psycopg
from psycopg.rows import dict_row


def required_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f"Missing required environment variable: {name}")
    return value


def connection_settings() -> dict[str, str | int]:
    return {
        "host": required_env("DB_HOST"),
        "port": int(os.getenv("DB_PORT", "5432")),
        "dbname": required_env("DB_NAME"),
        "user": required_env("DB_USER"),
        "password": required_env("DB_PASSWORD"),
        "connect_timeout": int(os.getenv("DB_CONNECT_TIMEOUT_SECONDS", "3")),
    }


@contextmanager
def get_connection():
    with psycopg.connect(**connection_settings(), row_factory=dict_row) as connection:
        yield connection


def initialize_schema() -> None:
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS tasks (
                    id SERIAL PRIMARY KEY,
                    title TEXT NOT NULL,
                    description TEXT,
                    processed BOOLEAN NOT NULL DEFAULT FALSE,
                    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                    processed_at TIMESTAMPTZ
                );
                """
            )
        connection.commit()


def database_ready() -> bool:
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1 AS ok;")
            row = cursor.fetchone()
            return row["ok"] == 1


def list_tasks() -> list[dict[str, Any]]:
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT id, title, description, processed, created_at, processed_at
                FROM tasks
                ORDER BY id ASC;
                """
            )
            rows = cursor.fetchall()

    return [dict(row) for row in rows]


def create_task(title: str, description: str | None) -> dict[str, Any]:
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO tasks (title, description)
                VALUES (%s, %s)
                RETURNING id, title, description, processed, created_at, processed_at;
                """,
                (title, description),
            )
            row = cursor.fetchone()
        connection.commit()

    return dict(row)

