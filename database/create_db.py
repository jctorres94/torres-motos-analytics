from __future__ import annotations

import os

import psycopg2
from psycopg2 import sql
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT


def create_database() -> None:
    # Preserve the database name already used by the Power BI file.
    database_name = os.getenv("POSTGRES_DB", "torres_motors_db")
    connection = psycopg2.connect(
        dbname="postgres",
        user=os.getenv("POSTGRES_USER", "postgres"),
        password=os.environ["POSTGRES_PASSWORD"],
        host=os.getenv("POSTGRES_HOST", "localhost"),
        port=os.getenv("POSTGRES_PORT", "5432"),
    )
    connection.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT 1 FROM pg_database WHERE datname = %s", (database_name,)
            )
            if cursor.fetchone():
                print(f"Database {database_name!r} already exists.")
                return
            cursor.execute(sql.SQL("CREATE DATABASE {}").format(sql.Identifier(database_name)))
            print(f"Database {database_name!r} created successfully.")
    finally:
        connection.close()


if __name__ == "__main__":
    create_database()
