"""
This file should be used to migrate the db from its current state to the
new state. This file should only be used once.
"""

import re
import sqlite3

db = sqlite3.connect("util/database.sqlite")
c = db.cursor()

"""
escape invalid regex
"""
c.execute("SELECT uid, message FROM alert")
for uid, message in c.fetchall():
    try:
        re.compile(message)
    except re.error:
        c.execute(
            "UPDATE alerts SET message = ? WHERE uid = ? AND message = ?",
            (re.escape(message), uid, message),
        )

db.commit()
db.close()
