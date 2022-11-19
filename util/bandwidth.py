from typing import Literal
import sqlite3
from datetime import datetime

database = sqlite3.connect("bandwidth.db")

# setup the table
database.cursor().execute(
    "CREATE TABLE IF NOT EXISTS bandwidth (timestamp DATETIME, bytes INTEGER, direction TEXT, category TEXT, detail TEXT)"
)
database.commit()

# logs bandwidth that gets used
def log(
    bytes: int | float,  # how many bytes were used?
    direction: Literal["inbound"] | Literal["outbound"],  # inbound = download, outbound = upload
    category: str | None = None,  # very general description of the type of usage (i.e. "download_attachment")
    detail: str | None = None,  # specific description of the usage (i.e. "HTTP GET http://url.com")
) -> None:
    cursor = database.cursor()

    cursor.execute(
        "INSERT INTO bandwidth (timestamp, bytes, direction, category, detail) VALUES (?, ?, ?, ?, ?)",
        (datetime.now(), bytes, direction, category, detail),
    )

    database.commit()
