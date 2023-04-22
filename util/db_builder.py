"""
Builds the database from scratch if it doesn't exist
this file is used on import in main.py and should not be run manually
Author: !SKA#0001
"""

import sqlite3

db = sqlite3.connect("util/database.sqlite")
c = db.cursor()

c.execute(
    """
    CREATE TABLE IF NOT EXISTS user (
    uid INTEGER PRIMARY KEY,
    messagesSent INTEGER NOT NULL,
    markedSpam BOOLEAN NOT NULL,
    cooldown varchar(100),
    helpMessagesSent INTEGER NOT NULL
    );
    """,
)

c.execute(
    """
    CREATE TABLE IF NOT EXISTS status (
    statusId INTEGER PRIMARY KEY,
    description VARCHAR(100) NOT NULL
    );
    """,
)

# 2000 is the discord message limit (lets not care about nitro for now)
c.execute(
    """
    CREATE TABLE IF NOT EXISTS alert (
    alertId INTEGER PRIMARY KEY,
    uid INTEGER NOT NULL,
    message VARCHAR(2000) NOT NULL,
    CONSTRAINT FK3_alert_user
		FOREIGN KEY (uid)
        REFERENCES user(uid)
    );
    """,
)

c.execute(
    """
    CREATE TABLE IF NOT EXISTS application (
    appId INTEGER PRIMARY KEY,
    uid INTEGER,
    status INTEGER,
    discordName VARCHAR(33),
    firstName VARCHAR(100),
    nda BOOLEAN,
    timezone VARCHAR(100),
    hoursAvailableWk VARCHAR(100),
    staffReason VARCHAR(4000),
    contributeReason VARCHAR(4000),
    submissionTime VARCHAR(100),
    CONSTRAINT FK1_application_user
		FOREIGN KEY (uid)
        REFERENCES user(uid),
    CONSTRAINT FK4_application_status
		FOREIGN KEY (status)
        REFERENCES status(statusId)
    );
    """,
)

c.execute(
    """
    CREATE TABLE IF NOT EXISTS like (
    likeId INTEGER PRIMARY KEY,
    appId INTEGER,
    uid INTEGER Nna,
    name VARCHAR(33),
    likes BOOLEAN Nna,
    CONSTRAINT FK2_like_application
        FOREIGN KEY (appID)
        REFERENCES application(appId)
    );
    """,
)

db.commit()
