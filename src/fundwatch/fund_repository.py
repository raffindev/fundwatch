from psycopg import Connection


def get_or_create_fund(cnpj: str, class_type: str, connection: Connection) -> int:
    with connection.cursor() as cursor:
        cursor.execute(
            """
            SELECT id
            FROM funds
            WHERE cnpj = %s
            """,
            (cnpj,),
        )

        fund_row = cursor.fetchone()

        if fund_row is not None:
            return fund_row[0]

        cursor.execute(
            """
            INSERT INTO funds (cnpj, class_type)
            VALUES (%s, %s)
            ON CONFLICT (cnpj) DO NOTHING
            RETURNING id
            """,
            (cnpj, class_type),
        )

        new_fund_id = cursor.fetchone()
        if new_fund_id is not None:
            return new_fund_id[0]

        cursor.execute(
            """
            SELECT id
            FROM funds
            WHERE cnpj = %s
            """,
            (cnpj,),
        )

        fund_row = cursor.fetchone()

        if fund_row is not None:
            return fund_row[0]

        raise RuntimeError(
            f"Failed to retrieve fund ID after insert conflict. CNPJ: {cnpj}"
        )
