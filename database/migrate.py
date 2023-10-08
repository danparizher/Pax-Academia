"""
This file should be used to migrate the db from its current state to the
new state. This file should only be used once, via the terminal.
"""

import sqlite3

import schema

db = sqlite3.connect(schema.file_path)
c = db.cursor()

"""
Alter table to include a new column
"""
c.execute(
    """
ALTER TABLE alert
ADD paused BOOLEAN;
""",
)

db.commit()
db.close()
