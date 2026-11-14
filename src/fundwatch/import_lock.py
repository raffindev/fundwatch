from psycopg import Connection


def acquire_import_lock(file_hash: str, connection: Connection) -> None:
    lock_key = int(file_hash[:16], 16)

    if lock_key >= 2**63:
        lock_key -= 2**64

    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT pg_advisory_xact_lock(%s)",
            (lock_key,),
        )
