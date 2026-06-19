import os
from contextlib import contextmanager

import psycopg


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
    with psycopg.connect(**connection_settings()) as connection:
        yield connection


def database_ready() -> bool:
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1;")
            return cursor.fetchone()[0] == 1


def process_tasks(batch_size: int = 5) -> int:
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                WITH next_tasks AS (
                    SELECT id
                    FROM tasks
                    WHERE processed = FALSE
                    ORDER BY id ASC
                    LIMIT %s
                    FOR UPDATE SKIP LOCKED
                )
                UPDATE tasks
                SET processed = TRUE,
                    processed_at = NOW()
                WHERE id IN (SELECT id FROM next_tasks)
                RETURNING id;
                """,
                (batch_size,),
            )
            processed_count = len(cursor.fetchall())
        connection.commit()

    return processed_count

