from datetime import date
from psycopg import Connection


def get_current_daily_report(
    fund_id: int,
    reference_date: date,
    subclass_id: str | None,
    connection: Connection,
) -> tuple | None:
    with connection.cursor() as cursor:
        cursor.execute(
            """
            SELECT
                id,
                total_value,
                quota_value,
                net_equity,
                inflow,
                outflow,
                shareholders
            FROM daily_reports
            WHERE fund_id = %s
              AND reference_date = %s
              AND subclass_id IS NOT DISTINCT FROM %s
              AND is_current = TRUE
            """,
            (fund_id, reference_date, subclass_id),
        )

        return cursor.fetchone()


def insert_daily_report(
    record: dict,
    fund_id: int,
    import_run_id: int,
    connection: Connection,
    revision_id: int | None = None,
) -> int:
    with connection.cursor() as cursor:
        cursor.execute(
            """
            INSERT INTO daily_reports (
                fund_id,
                subclass_id,
                reference_date,
                total_value,
                quota_value,
                net_equity,
                inflow,
                outflow,
                shareholders,
                import_run_id,
                revision_id
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id
            """,
            (
                fund_id,
                record["subclass_id"],
                record["reference_date"],
                record["total_value"],
                record["quota_value"],
                record["net_equity"],
                record["inflow"],
                record["outflow"],
                record["shareholders"],
                import_run_id,
                revision_id,
            ),
        )

        result = cursor.fetchone()

        if result is None:
            raise RuntimeError("Failed to retrieve inserted daily report ID.")

        return result[0]


def reports_are_equal(current_report: tuple, record: dict) -> bool:
    current_values = current_report[1:]

    new_values = (
        record["total_value"],
        record["quota_value"],
        record["net_equity"],
        record["inflow"],
        record["outflow"],
        record["shareholders"],
    )

    return current_values == new_values


def deactivate_current_daily_report(
    report_id: int,
    connection: Connection,
) -> None:
    with connection.cursor() as cursor:
        cursor.execute(
            """
            UPDATE daily_reports
            SET is_current = FALSE
            WHERE id = %s
            AND is_current = TRUE
            """,
            (report_id,),
        )

        if cursor.rowcount != 1:
            raise RuntimeError(
                f"Failed to deactivate current daily report. ID: {report_id}"
            )


def create_revision(
    import_run_id: int,
    reference_date: date,
    note: str,
    connection: Connection,
) -> int:
    with connection.cursor() as cursor:
        cursor.execute(
            """
            INSERT INTO revisions (run_id, reference_date, note)
            VALUES (%s, %s, %s)
            RETURNING id
            """,
            (import_run_id, reference_date, note),
        )

        result = cursor.fetchone()

        if result is None:
            raise RuntimeError("Failed to retrieve created revision ID.")

        return result[0]
