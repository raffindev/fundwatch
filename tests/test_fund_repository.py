import pytest

from fundwatch.database import get_connection
from fundwatch.fund_repository import get_or_create_fund


@pytest.fixture
def connection():
    conn = get_connection(
        db_name="sql_lab",
        schema="fundwatch_test",
    )

    try:
        yield conn
    finally:
        conn.rollback()
        conn.close()


def test_get_or_create_fund(connection):
    cnpj = "12345678000190"
    class_type = "1"

    first_fund_id = get_or_create_fund(
        cnpj=cnpj,
        class_type=class_type,
        connection=connection,
    )

    second_fund_id = get_or_create_fund(
        cnpj=cnpj,
        class_type=class_type,
        connection=connection,
    )

    assert isinstance(first_fund_id, int)
    assert first_fund_id == second_fund_id

    with connection.cursor() as cursor:
        cursor.execute(
            """
            SELECT COUNT(*)
            FROM funds
            WHERE cnpj = %s
            """,
            (cnpj,),
        )

        result = cursor.fetchone()

    assert result is not None
    assert result[0] == 1


def test_get_existing_fund(connection):
    cnpj = "98765432000110"
    class_type = "1"

    with connection.cursor() as cursor:
        cursor.execute(
            """
            INSERT INTO funds (cnpj, class_type)
            VALUES (%s, %s)
            RETURNING id
            """,
            (cnpj, class_type),
        )

        result = cursor.fetchone()

    assert result is not None
    expected_id = result[0]

    fund_id = get_or_create_fund(
        cnpj=cnpj,
        class_type=class_type,
        connection=connection,
    )

    assert fund_id == expected_id
