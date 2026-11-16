from decimal import Decimal
from pathlib import Path

import pytest

from fundwatch.database import get_connection
from fundwatch.import_service import import_cvm_file

DB_NAME = "sql_lab"
TEST_SCHEMA = "fundwatch_test"

CSV_HEADER = (
    "TP_FUNDO_CLASSE;CNPJ_FUNDO_CLASSE;ID_SUBCLASSE;"
    "DT_COMPTC;VL_TOTAL;VL_QUOTA;VL_PATRIM_LIQ;"
    "CAPTC_DIA;RESG_DIA;NR_COTST\n"
)

FIRST_RECORD = (
    "1;12345678000190;;2026-10-15;1750000.50;"
    "1.234567890123;1500000.75;50000.00;25000.00;150\n"
)
SECOND_RECORD = (
    "1;98765432000110;;2026-10-15;2500000.00;"
    "2.345678901234;2200000.00;75000.00;30000.00;200\n"
)
REVISED_RECORD = FIRST_RECORD.replace("1500000.75", "1600000.75")
INVALID_DATE_RECORD = SECOND_RECORD.replace("2026-10-15", "2026-02-30")


def run_import(file_path: Path) -> int:
    return import_cvm_file(
        file_path=file_path,
        schema=TEST_SCHEMA,
        db_name=DB_NAME,
    )


@pytest.fixture
def csv_factory(tmp_path: Path):
    def create_csv(filename: str, *records: str, suffix: str = "") -> Path:
        csv_file = tmp_path / filename
        csv_file.write_text(
            CSV_HEADER + "".join(records) + suffix,
            encoding="utf-8",
        )
        return csv_file

    return create_csv


@pytest.fixture
def db_connection():
    with get_connection(db_name=DB_NAME, schema=TEST_SCHEMA) as connection:
        yield connection


@pytest.fixture
def clean_database():
    def clear_tables():
        with get_connection(db_name=DB_NAME, schema=TEST_SCHEMA) as connection:
            with connection.cursor() as cursor:
                cursor.execute("""
                    TRUNCATE TABLE
                        import_attempts,
                        daily_reports,
                        revisions,
                        funds,
                        import_runs
                    RESTART IDENTITY CASCADE
                    """)

    clear_tables()
    try:
        yield
    finally:
        clear_tables()


def test_import_cvm_file_success(csv_factory, clean_database, db_connection):
    csv_file = csv_factory("valid_import.csv", FIRST_RECORD, SECOND_RECORD)
    import_run_id = run_import(csv_file)

    with db_connection.cursor() as cursor:
        cursor.execute(
            """
            SELECT status, total_records, duplicates, missing_subclass
            FROM import_runs WHERE id = %s
            """,
            (import_run_id,),
        )
        import_result = cursor.fetchone()
        cursor.execute(
            "SELECT COUNT(*) FROM daily_reports WHERE import_run_id = %s",
            (import_run_id,),
        )
        report_count = cursor.fetchone()[0]

    assert import_result == ("SUCCESS", 2, 0, 2)
    assert report_count == 2


def test_import_cvm_file_already_imported(csv_factory, clean_database, db_connection):
    csv_file = csv_factory("duplicate_import.csv", FIRST_RECORD)
    first_run_id = run_import(csv_file)

    with pytest.raises(ValueError, match="File has already been successfully imported"):
        run_import(csv_file)

    with db_connection.cursor() as cursor:
        cursor.execute("SELECT COUNT(*) FROM import_runs")
        run_count = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM daily_reports")
        report_count = cursor.fetchone()[0]
        cursor.execute("SELECT outcome, import_run_id FROM import_attempts ORDER BY id")
        attempts = cursor.fetchall()

    assert isinstance(first_run_id, int)
    assert run_count == 1
    assert report_count == 1
    assert attempts == [
        ("ACCEPTED", first_run_id),
        ("ALREADY_IMPORTED", None),
    ]


def test_import_cvm_file_duplicate_records(csv_factory, clean_database, db_connection):
    csv_file = csv_factory("duplicate_records.csv", FIRST_RECORD, FIRST_RECORD)

    with pytest.raises(ValueError, match="Duplicate record in CSV"):
        run_import(csv_file)

    with db_connection.cursor() as cursor:
        cursor.execute("""
            SELECT status, total_records, duplicates, error_message
            FROM import_runs
            """)
        import_result = cursor.fetchone()
        cursor.execute("SELECT COUNT(*) FROM funds")
        fund_count = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM daily_reports")
        report_count = cursor.fetchone()[0]
        cursor.execute("SELECT outcome FROM import_attempts")
        attempt = cursor.fetchone()

    assert import_result is not None
    assert import_result[0] == "FAILED"
    assert import_result[1] == 2
    assert import_result[2] == 1
    assert "Duplicate record in CSV" in import_result[3]
    assert fund_count == 0
    assert report_count == 0
    assert attempt == ("ACCEPTED",)


def test_import_cvm_file_invalid_record(csv_factory, clean_database, db_connection):
    csv_file = csv_factory("invalid_record.csv", FIRST_RECORD, INVALID_DATE_RECORD)

    with pytest.raises(ValueError):
        run_import(csv_file)

    with db_connection.cursor() as cursor:
        cursor.execute("SELECT status, total_records, error_message FROM import_runs")
        result = cursor.fetchone()
        cursor.execute("SELECT COUNT(*) FROM funds")
        fund_count = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM daily_reports")
        report_count = cursor.fetchone()[0]

    assert result is not None
    assert result[0] == "FAILED"
    assert result[1] == 1
    assert "DT_COMPTC" in result[2]
    assert fund_count == 0
    assert report_count == 0


def test_import_cvm_file_creates_revision(csv_factory, clean_database, db_connection):
    original_file = csv_factory("original.csv", FIRST_RECORD)
    revised_file = csv_factory("revised.csv", REVISED_RECORD)

    first_run_id = run_import(original_file)
    second_run_id = run_import(revised_file)

    with db_connection.cursor() as cursor:
        cursor.execute("""
            SELECT import_run_id, net_equity, is_current, revision_id
            FROM daily_reports ORDER BY id
            """)
        reports = cursor.fetchall()
        cursor.execute("SELECT run_id FROM revisions")
        revisions = cursor.fetchall()
        cursor.execute("SELECT COUNT(*) FROM funds")
        fund_count = cursor.fetchone()[0]

    assert fund_count == 1
    assert len(reports) == 2
    assert reports[0] == (first_run_id, Decimal("1500000.75"), False, None)
    assert reports[1][:3] == (second_run_id, Decimal("1600000.75"), True)
    assert reports[1][3] is not None
    assert revisions == [(second_run_id,)]


def test_import_cvm_file_unchanged_report(csv_factory, clean_database, db_connection):
    first_file = csv_factory("first.csv", FIRST_RECORD)
    # Mudança no conteúdo bruto, mas não nos valores financeiros.
    second_file = csv_factory("second.csv", FIRST_RECORD, suffix="\n")

    first_run_id = run_import(first_file)
    second_run_id = run_import(second_file)

    with db_connection.cursor() as cursor:
        cursor.execute("SELECT COUNT(*) FROM daily_reports")
        report_count = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM revisions")
        revision_count = cursor.fetchone()[0]
        cursor.execute("SELECT id, status FROM import_runs ORDER BY id")
        runs = cursor.fetchall()

    assert report_count == 1
    assert revision_count == 0
    assert runs == [
        (first_run_id, "SUCCESS"),
        (second_run_id, "SUCCESS"),
    ]


def test_import_cvm_file_header_only(csv_factory, clean_database, db_connection):
    csv_file = csv_factory("header_only.csv")
    import_run_id = run_import(csv_file)

    with db_connection.cursor() as cursor:
        cursor.execute(
            """
            SELECT status, total_records, duplicates, missing_subclass
            FROM import_runs WHERE id = %s
            """,
            (import_run_id,),
        )
        result = cursor.fetchone()
        cursor.execute("SELECT COUNT(*) FROM daily_reports")
        report_count = cursor.fetchone()[0]

    assert result == ("SUCCESS", 0, 0, 0)
    assert report_count == 0
