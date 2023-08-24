import sqlite3
from dataclasses import dataclass

# Create the database and its tables, if they don't already exist.
from .schema import file_path


def connect() -> sqlite3.Connection:
    """
    simple shortcut for connecting to the sqlite file
    """
    return sqlite3.connect(file_path)


@dataclass
class TableInfo:
    name: str
    column_names: list[str]


def grep_tables() -> list[TableInfo]:
    """
    :return: A list of `TableInfo`s containing the names of each table and their columns.
    """
    tables: list[TableInfo] = []

    with connect() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT
                name
            FROM
                sqlite_schema
            WHERE
                type ='table'
                AND
                name NOT LIKE 'sqlite_%'
            """,
        )

        for (table_name,) in cursor.fetchall():
            cursor.execute(f"PRAGMA table_info({table_name})")
            tables.append(
                TableInfo(
                    name=table_name,
                    column_names=[x[1] for x in cursor.fetchall()],
                ),
            )

    return tables
