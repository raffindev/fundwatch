from src.fundwatch.database import get_connection
from src.fundwatch.import_repository import (
    create_import_run,
    has_successful_import,
    update_import_run,
    create_import_attempt,
)


def test_create_import_run():
    connection = get_connection(
        db_name="sql_lab",
        schema="fundwatch_test",
    )

    try:
        # Inserção do registro
        import_run_id = create_import_run(
            filename="test_import.csv",
            file_hash="a" * 64,
            connection=connection,
        )

        # Verificação do registro inserido
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT filename, file_hash, status
                FROM import_runs
                WHERE id = %s
                """,
                (import_run_id,),
            )

            result = cursor.fetchone()

        assert result == (
            "test_import.csv",
            "a" * 64,
            "PROCESSING",
        )

    finally:
        connection.rollback()
        connection.close()


import pytest


@pytest.mark.parametrize(
    "status, expected",
    [
        (None, False),
        ("PROCESSING", False),
        ("FAILED", False),
        ("REJECTED", False),
        ("SUCCESS", True),
    ],
)
def test_has_successful_import(status, expected):
    connection = get_connection(
        db_name="sql_lab",
        schema="fundwatch_test",
    )

    try:
        file_hash = "b" * 64

        if status is not None:
            import_run_id = create_import_run(
                filename="test_import.csv",
                file_hash=file_hash,
                connection=connection,
            )

            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    UPDATE import_runs
                    SET status = %s,
                        finished_at = CURRENT_TIMESTAMP
                    WHERE id = %s
                    """,
                    (status, import_run_id),
                )

        result = has_successful_import(
            file_hash=file_hash,
            connection=connection,
        )

        assert result is expected

    finally:
        connection.rollback()
        connection.close()


@pytest.mark.parametrize(
    "status",
    ["SUCCESS", "FAILED", "REJECTED"],
)
def test_update_import_run(status):
    connection = get_connection(
        db_name="sql_lab",
        schema="fundwatch_test",
    )

    try:
        import_run_id = create_import_run(
            filename="update_test.csv",
            file_hash="c" * 64,
            connection=connection,
        )

        update_import_run(
            import_run_id=import_run_id,
            status=status,
            total_records=100,
            duplicates=2,
            missing_subclass=5,
            connection=connection,
        )

        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT status, total_records, duplicates,
                       missing_subclass, finished_at
                FROM import_runs
                WHERE id = %s
                """,
                (import_run_id,),
            )

            result = cursor.fetchone()

        assert result[:4] == (status, 100, 2, 5)
        assert result[4] is not None

    finally:
        connection.rollback()
        connection.close()


@pytest.mark.parametrize(
    "status, total_records, duplicates, missing_subclass",
    [
        ("PROCESSING", 100, 0, 0),
        ("INVALID", 100, 0, 0),
        ("SUCCESS", -1, 0, 0),
        ("SUCCESS", 100, -1, 0),
        ("SUCCESS", 100, 0, -1),
    ],
)
def test_update_import_run_invalid_inputs(
    status, total_records, duplicates, missing_subclass
):
    connection = get_connection(
        db_name="sql_lab",
        schema="fundwatch_test",
    )

    try:
        import_run_id = create_import_run(
            filename="invalid_update.csv",
            file_hash="d" * 64,
            connection=connection,
        )

        with pytest.raises(ValueError):
            update_import_run(
                import_run_id=import_run_id,
                status=status,
                total_records=total_records,
                duplicates=duplicates,
                missing_subclass=missing_subclass,
                connection=connection,
            )

    finally:
        connection.rollback()
        connection.close()


@pytest.mark.parametrize("status", ["SUCCESS", "FAILED"])
def test_update_import_run_already_finalized(status):
    connection = get_connection(
        db_name="sql_lab",
        schema="fundwatch_test",
    )

    try:
        import_run_id = create_import_run(
            filename="invalid_update.csv",
            file_hash="d" * 64,
            connection=connection,
        )

        # Primeira atualização: válida
        update_import_run(
            import_run_id=import_run_id,
            status="SUCCESS",
            connection=connection,
        )

        # Segunda atualização: deve ser rejeitada
        with pytest.raises(ValueError):
            update_import_run(
                import_run_id=import_run_id,
                status=status,
                connection=connection,
            )

        # Confirma que o registro não foi alterado
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT status
                FROM import_runs
                WHERE id = %s
                """,
                (import_run_id,),
            )
            result = cursor.fetchone()

        assert result[0] == "SUCCESS"

    finally:
        connection.rollback()
        connection.close()


def test_update_import_run_not_found():
    connection = get_connection(
        db_name="sql_lab",
        schema="fundwatch_test",
    )

    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT COALESCE(MAX(id), 0) + 1 FROM import_runs")
            nonexistent_id = cursor.fetchone()[0]

        with pytest.raises(ValueError, match="does not exist"):
            update_import_run(
                import_run_id=nonexistent_id,
                status="SUCCESS",
                connection=connection,
            )

    finally:
        connection.rollback()
        connection.close()


def test_create_import_attempt_rejected():
    connection = get_connection(
        db_name="sql_lab",
        schema="fundwatch_test",
    )

    try:
        attempt_id = create_import_attempt(
            filename="test_import.csv",
            file_hash="a" * 64,
            target_table="daily_reports",
            outcome="REJECTED",
            reason="Invalid import request.",
            connection=connection,
        )

        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT filename, outcome, import_run_id, reason
                FROM import_attempts
                WHERE id = %s
                """,
                (attempt_id,),
            )

            record = cursor.fetchone()

        assert record[0] == "test_import.csv"
        assert record[1] == "REJECTED"
        assert record[2] is None
        assert record[3] == "Invalid import request."

    finally:
        connection.rollback()
        connection.close()


def test_create_import_attempt_accepted():
    connection = get_connection(
        db_name="sql_lab",
        schema="fundwatch_test",
    )

    try:
        import_run_id = create_import_run(
            filename="accepted_import.csv",
            file_hash="b" * 64,
            connection=connection,
        )

        attempt_id = create_import_attempt(
            filename="accepted_import.csv",
            file_hash="b" * 64,
            target_table="daily_reports",
            outcome="ACCEPTED",
            import_run_id=import_run_id,
            connection=connection,
        )

        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT outcome, import_run_id
                FROM import_attempts
                WHERE id = %s
                """,
                (attempt_id,),
            )

            record = cursor.fetchone()

        assert record[0] == "ACCEPTED"
        assert record[1] == import_run_id

    finally:
        connection.rollback()
        connection.close()


@pytest.mark.parametrize(
    "outcome, import_run_id",
    [
        ("PROCESSING", None),
        ("ACCEPTED", None),
        ("REJECTED", 15),
        ("ALREADY_IMPORTED", 15),
    ],
)
def test_create_import_attempt_invalid_inputs(outcome, import_run_id):
    with pytest.raises(ValueError):
        create_import_attempt(
            filename="invalid_attempt.csv",
            file_hash="c" * 64,
            target_table="daily_reports",
            outcome=outcome,
            import_run_id=import_run_id,
        )


def test_create_import_attempt_already_imported():
    connection = get_connection(db_name="sql_lab", schema="fundwatch_test")

    try:
        attempt_id = create_import_attempt(
            filename="already_imported.csv",
            file_hash="d" * 64,
            target_table="daily_reports",
            outcome="ALREADY_IMPORTED",
            reason="File has already been successfully imported.",
            connection=connection,
        )

        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT outcome, import_run_id
                FROM import_attempts
                WHERE id = %s
                """,
                (attempt_id,),
            )

            record = cursor.fetchone()

        assert record[0] == "ALREADY_IMPORTED"
        assert record[1] is None

    finally:
        connection.rollback()
        connection.close()
