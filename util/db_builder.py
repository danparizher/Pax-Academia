"""
Builds the database from scratch.
This file needs to be ran once before starting the bot for the first time
Author: !SKA#0001
"""

import sqlite3

db = sqlite3.connect("util/database.sqlite")
c = db.cursor()

c.execute(
    """
    CREATE TABLE IF NOT EXISTS user (
    uid INT PRIMARY KEY,
    messagesSent INT Nna,
    markedSpam BOOLEAN Nna,
    cooldown varchar(100)
    );
    """
)

c.execute(
    """
    CREATE TABLE IF NOT EXISTS status (
    statusId INT PRIMARY KEY,
    description VARCHAR(100)
    );
    """
)

# 2000 is the discord message limit (lets not care about nitro for now)
c.execute(
    """
    CREATE TABLE IF NOT EXISTS alert (
    alertId INT PRIMARY KEY,
    uid INT,
    message VARCHAR(2000),
    CONSTRAINT FK3_alert_user
		FOREIGN KEY (uid)
        REFERENCES user(uid)
    );
    """
)

c.execute(
    """
    CREATE TABLE IF NOT EXISTS application (
    appId INT PRIMARY KEY,
    uid INT,
    status INT,
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
    """
)

c.execute(
    """
    CREATE TABLE IF NOT EXISTS like (
    likeId INT PRIMARY KEY,
    appId INT,
    uid INT Nna,
    name VARCHAR(33),
    likes BOOLEAN Nna,
    CONSTRAINT FK2_like_application
        FOREIGN KEY (appID)
        REFERENCES application(appId)
    );
    """
)

db.commit()