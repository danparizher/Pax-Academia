"""
This file should be used to migrate the db from its current state to the
new state. This file should only be used once.
"""

import sqlite3

db = sqlite3.connect("util/database.sqlite")
c = db.cursor()


"""
Statusses:
1 = Application submitted
2 = Application Denied
3 = Second Opinion required
4 = Meets requirements
5 = Pending first interview
6 = Pending second interview
7 = Pending decision
8 = Pending onboardment
9 = Accepted
"""

data = [
    (
        1,
        "Application submitted",
    ),
    (
        2,
        "Application Denied",
    ),
    (
        3,
        "Second Opinion required",
    ),
    (
        4,
        "Meets requirements",
    ),
    (
        5,
        "Pending first interview",
    ),
    (
        6,
        "Pending second interview",
    ),
    (
        7,
        "Pending decision",
    ),
    (
        8,
        "Pending onboardment",
    ),
    (
        9,
        "Accepted",
    ),
]
# Add the new statusses
c.executemany("INSERT INTO status (statusId, description) VALUES (?, ?)", data)
db.commit()
db.close()
