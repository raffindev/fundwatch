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


def has_successful_import(
    file_hash: str,
    connection: Connection | None = None,
) -> bool:
    connection_context = (
        nullcontext(connection) if connection is not None else get_connection()
    )

    with connection_context as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                SELECT EXISTS (
                    SELECT 1
                    FROM import_runs
                    WHERE file_hash = %s
                      AND status = 'SUCCESS'
                )
                """,
                (file_hash,),
            )

            result = cursor.fetchone()

            return result[0]


def update_import_run(
    import_run_id: int,
    status: str,
    total_records: int | None = None,
    duplicates: int | None = None,
    missing_subclass: int | None = None,
    error_message: str | None = None,
    connection: Connection | None = None,
) -> None:
    allowed_statuses = {"SUCCESS", "FAILED", "REJECTED"}

    if status not in allowed_statuses:
        raise ValueError(f"Invalid final import status: {status}")

    for name, value in {
        "total_records": total_records,
        "duplicates": duplicates,
        "missing_subclass": missing_subclass,
    }.items():
        if value is not None and (type(value) is not int or value < 0):
            raise ValueError(f"{name} must be a non-negative integer.")

    connection_context = (
        nullcontext(connection) if connection is not None else get_connection()
    )

    with connection_context as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                UPDATE import_runs
                SET status = %s,
                    finished_at = CURRENT_TIMESTAMP,
                    total_records = %s,
                    duplicates = %s,
                    missing_subclass = %s,
                    error_message = %s
                WHERE id = %s
                  AND status = 'PROCESSING'
                RETURNING id
                """,
                (
                    status,
                    total_records,
                    duplicates,
                    missing_subclass,
                    error_message,
                    import_run_id,
                ),
            )

            result = cursor.fetchone()

            if result is None:
                raise ValueError(
                    f"Import run {import_run_id} does not exist "
                    "or is already finalized."
                )


def create_import_attempt(
    filename: str,
    file_hash: str,
    target_table: str,
    outcome: str,
    requested_by: str | None = None,
    import_run_id: int | None = None,
    reason: str | None = None,
    connection: Connection | None = None,
) -> int:
    allowed_outcomes = {"ACCEPTED", "ALREADY_IMPORTED", "REJECTED"}

    if outcome not in allowed_outcomes:
        raise ValueError(f"Invalid import attempt outcome: {outcome}")

    if outcome == "ACCEPTED" and import_run_id is None:
        raise ValueError("Accepted import attempts require an import run ID.")

    if outcome != "ACCEPTED" and import_run_id is not None:
        raise ValueError("Non-accepted import attempts must not have an import run ID.")

    connection_context = (
        nullcontext(connection) if connection is not None else get_connection()
    )
    with connection_context as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO import_attempts (
                    filename, file_hash, requested_by, target_table,
                    outcome, import_run_id, reason
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                RETURNING id
                """,
                (
                    filename,
                    file_hash,
                    requested_by,
                    target_table,
                    outcome,
                    import_run_id,
                    reason,
                ),
            )

            result = cursor.fetchone()
            return result[0]


def has_processing_import(
    file_hash: str,
    connection: Connection | None = None,
) -> bool:
    context = nullcontext(connection) if connection is not None else get_connection()

    with context as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                SELECT EXISTS (
                    SELECT 1
                    FROM import_runs
                    WHERE file_hash = %s
                      AND status = 'PROCESSING'
                )
                """,
                (file_hash,),
            )

            result = cursor.fetchone()
            return bool(result[0])
