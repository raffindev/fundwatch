import os
import psycopg
from dotenv import load_dotenv


def get_connection():
    load_dotenv()

    db_host = os.getenv("DB_HOST")
    db_port = os.getenv("DB_PORT")
    db_name = os.getenv("DB_NAME")
    db_user = os.getenv("DB_USER")
    db_password = os.getenv("DB_PASSWORD")

    connection = psycopg.connect(
        host=db_host, port=db_port, dbname=db_name, user=db_user, password=db_password
    )

    return connection
