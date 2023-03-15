"""
This file should be used to migrate the db from its current state to the
new state. This file should only be used once.
"""

import base64
import sqlite3


def b64ify(x: str) -> str:
    return base64.b64encode(x.encode()).decode()


def deb64ify(y: str) -> str:
    return base64.b64decode(y.encode()).decode()


"""
Data that needs to be migrated:
- alerts
keyword (b64)
user_id
author_name
=>
- alert
alertId
uid
message

- messagecount
uid
amount
=>
- user
uid
messagesSent
marked_spam
cooldown
"""

# Migrate all alerts
db_old = sqlite3.connect("util/database_old.sqlite")
db_new = sqlite3.connect("util/database.sqlite")
c_old = db_old.cursor()
c_new = db_new.cursor()

c_old.execute("SELECT * FROM alerts")
data = c_old.fetchall()
c_new.executemany(
    """
    INSERT INTO alert(uid, message) VALUES (?, ?)""",
    [(x[1], deb64ify(x[0])) for x in data],
)
db_new.commit()


# Migrate all message counts
c_old.execute("SELECT * FROM messagecount")
data = c_old.fetchall()
c_new.executemany(
    """
    INSERT INTO user(uid, messagesSent, markedSpam, cooldown) VALUES (?, ?, ?, ?)""",
    [(x[0], x[1], False, None) for x in data],
)
db_new.commit()
