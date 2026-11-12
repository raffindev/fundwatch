from src.fundwatch.database import get_connection
from src.fundwatch.import_repository import create_import_run


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
