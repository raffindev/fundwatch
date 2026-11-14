from pathlib import Path

from .file_hash import calculate_file_hash
from .database import get_connection
from .import_lock import acquire_import_lock
from .import_repository import (
    has_successful_import,
    has_processing_import,
    create_import_attempt,
    create_import_run,
)


def import_cvm_file(file_path: Path) -> int:
    if not file_path.is_file():
        raise FileNotFoundError(f"File not found: {file_path}")

    file_hash = calculate_file_hash(file_path)
    with get_connection() as connection:

        acquire_import_lock(file_hash, connection)
        processing_import = has_processing_import(
            file_hash,
            connection=connection,
        )

        already_imported = has_successful_import(file_hash, connection=connection)

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
                reason="File import rejected: another import of this file is already in progress.",
                connection=connection,
            )

        else:
            import_run_id = create_import_run(
                file_path.name, file_hash, connection=connection
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
        raise ValueError(
            "File import rejected: another import of this file is already in progress."
        )
