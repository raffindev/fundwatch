from contextlib import nullcontext

from psycopg import Connection

from .database import get_connection


def create_import_run(
    filename: str,
    file_hash: str,
    connection: Connection | None = None,
) -> int:
    connection_context = (
        nullcontext(connection) if connection is not None else get_connection()
    )

    with connection_context as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO import_runs (filename, file_hash, status)
                VALUES (%s, %s, %s)
                RETURNING id
                """,
                (filename, file_hash, "PROCESSING"),
            )

            result = cursor.fetchone()
            import_run_id = result[0]

    return import_run_id
