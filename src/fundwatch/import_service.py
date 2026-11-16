from pathlib import Path

from psycopg import Connection

from .database import get_connection
from .file_hash import calculate_file_hash
from .record_reader import read_validated_records

from .import_repository import (
    has_successful_import,
    has_processing_import,
    create_import_attempt,
    create_import_run,
    update_import_run,
)

from .fund_repository import get_or_create_fund

from .daily_report_repository import (
    get_current_daily_report,
    insert_daily_report,
    reports_are_equal,
    deactivate_current_daily_report,
    create_revision,
)

IMPORT_LOCK_KEY = 824017351


def acquire_global_import_lock(connection: Connection) -> None:
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT pg_advisory_xact_lock(%s)",
            (IMPORT_LOCK_KEY,),
        )


def process_daily_report(
    record: dict,
    import_run_id: int,
    connection: Connection,
) -> str:
    fund_id = get_or_create_fund(
        cnpj=record["cnpj"],
        class_type=record["class_type"],
        connection=connection,
    )

    current_report = get_current_daily_report(
        fund_id=fund_id,
        reference_date=record["reference_date"],
        subclass_id=record["subclass_id"],
        connection=connection,
    )

    if current_report is None:
        insert_daily_report(
            record=record,
            fund_id=fund_id,
            import_run_id=import_run_id,
            connection=connection,
        )
        return "INSERTED"

    if reports_are_equal(current_report, record):
        return "UNCHANGED"

    revision_id = create_revision(
        import_run_id=import_run_id,
        reference_date=record["reference_date"],
        note="Financial values changed in a subsequent CVM import.",
        connection=connection,
    )

    deactivate_current_daily_report(
        report_id=current_report[0],
        connection=connection,
    )

    insert_daily_report(
        record=record,
        fund_id=fund_id,
        import_run_id=import_run_id,
        revision_id=revision_id,
        connection=connection,
    )

    return "REVISED"


def import_cvm_file(
    file_path: Path,
    schema: str = "fundwatch",
    db_name: str | None = None,
) -> int:
    file_path = Path(file_path)

    if not file_path.is_file():
        raise FileNotFoundError(f"File not found: {file_path}")

    file_hash = calculate_file_hash(file_path)

    # --------------------------------------------------
    # 1. Initial audit
    # --------------------------------------------------

    with get_connection(
        db_name=db_name,
        schema=schema,
    ) as connection:

        acquire_global_import_lock(connection)

        already_imported = has_successful_import(
            file_hash,
            connection=connection,
        )

        processing_import = has_processing_import(
            file_hash,
            connection=connection,
        )

        if already_imported:
            create_import_attempt(
                filename=file_path.name,
                file_hash=file_hash,
                target_table="daily_reports",
                outcome="ALREADY_IMPORTED",
                reason="File has already been successfully imported.",
                connection=connection,
            )

        elif processing_import:
            create_import_attempt(
                filename=file_path.name,
                file_hash=file_hash,
                target_table="daily_reports",
                outcome="REJECTED",
                reason="Another import of this file is already in progress.",
                connection=connection,
            )

        else:
            import_run_id = create_import_run(
                filename=file_path.name,
                file_hash=file_hash,
                connection=connection,
            )

            create_import_attempt(
                filename=file_path.name,
                file_hash=file_hash,
                target_table="daily_reports",
                outcome="ACCEPTED",
                import_run_id=import_run_id,
                connection=connection,
            )

    if already_imported:
        raise ValueError("File has already been successfully imported.")

    if processing_import:
        raise ValueError("File import rejected: another import is already in progress.")

    # --------------------------------------------------
    # 2. Processing of records
    # --------------------------------------------------

    total_records = 0
    inserted = 0
    unchanged = 0
    revised = 0
    duplicates = 0
    missing_subclass = 0

    seen_keys = set()

    try:
        with get_connection(
            db_name=db_name,
            schema=schema,
        ) as connection:

            acquire_global_import_lock(connection)

            for record in read_validated_records(file_path):
                total_records += 1

                record_key = (
                    record["cnpj"],
                    record["subclass_id"],
                    record["reference_date"],
                )

                if record_key in seen_keys:
                    duplicates += 1

                    raise ValueError(
                        "Duplicate record in CSV: "
                        f"CNPJ={record['cnpj']}, "
                        f"subclass={record['subclass_id']}, "
                        f"date={record['reference_date']}"
                    )

                seen_keys.add(record_key)

                if record["subclass_id"] is None:
                    missing_subclass += 1

                result = process_daily_report(
                    record=record,
                    import_run_id=import_run_id,
                    connection=connection,
                )

                if result == "INSERTED":
                    inserted += 1

                elif result == "UNCHANGED":
                    unchanged += 1

                elif result == "REVISED":
                    revised += 1

                else:
                    raise RuntimeError(f"Unexpected daily report result: {result}")

            update_import_run(
                import_run_id=import_run_id,
                status="SUCCESS",
                total_records=total_records,
                duplicates=duplicates,
                missing_subclass=missing_subclass,
                connection=connection,
            )

    except Exception as exc:
        with get_connection(
            db_name=db_name,
            schema=schema,
        ) as connection:

            update_import_run(
                import_run_id=import_run_id,
                status="FAILED",
                total_records=total_records,
                duplicates=duplicates,
                missing_subclass=missing_subclass,
                error_message=str(exc),
                connection=connection,
            )

        raise

    # --------------------------------------------------
    # 3. Result
    # --------------------------------------------------

    print(
        f"Import run: {import_run_id} | "
        f"Total: {total_records} | "
        f"Inserted: {inserted} | "
        f"Unchanged: {unchanged} | "
        f"Revised: {revised} | "
        f"Duplicates: {duplicates} | "
        f"Missing subclasses: {missing_subclass}"
    )

    return import_run_id
