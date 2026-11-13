import os

import psycopg
from dotenv import load_dotenv


def get_connection(
    db_name: str | None = None,
    schema: str | None = None,
):
    load_dotenv()

    db_host = os.getenv("DB_HOST")
    db_port = os.getenv("DB_PORT")
    database_name = db_name or os.getenv("DB_NAME")
    db_user = os.getenv("DB_USER")
    db_password = os.getenv("DB_PASSWORD")

    connection = psycopg.connect(
        host=db_host,
        port=db_port,
        dbname=database_name,
        user=db_user,
        password=db_password,
        options="-c search_path=fundwatch_test" if schema == "fundwatch_test" else None,
    )

    return connection
