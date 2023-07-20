"""
This file should be used to migrate the db from its current state to the
new state. This file should only be used once.
"""

import sqlite3

db = sqlite3.connect("util/database.sqlite")
c = db.cursor()

"""
Alter table to include a new column
"""
c.execute(
    """
ALTER TABLE alert
ADD COLUMN paused BOOLEAN DEFAULT FALSE;
""",
)

db.commit()
db.close()
