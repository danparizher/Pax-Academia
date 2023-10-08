# Database
This bot persists data in a single SQLite database (which is a file in this directory).

### Keeping Your Local Database Up-to-Date
- [`schema.py`](./schema.py) is responsible for creating the database & its tables.
It will not overwrite any existing tables.
This file is executed every time that the bot runs, so you don't need to worry about running it manually.
- [`migrate.py`](./migrate.py) is responsible for updating an old database to a new format. It should run **once** after
a schema change occurs via the terminal. Be careful not to miss a schema update, or you may need to delete your database
file and let [`schema.py`](./schema.py) create it again from scratch (losing all your data).


### Making a Change to the Production Database
- Update [`schema.py`](./schema.py) so that it can create a database in the correct state, from scratch.
- Overwrite [`migrate.py`](./migrate.py) such that it applies your change to the previous version of your database.
- Regenerate [`ERD.mdj`](./ERD.mdj). Reach out to @skagame on Discord if you need help with this.

For example, if you wanted to add an integer column named `reputation` to the `user` table,
you would add this line to [`schema.py`](./schema.py):
```diff
  c.execute(
      """
      CREATE TABLE IF NOT EXISTS user (
      uid INTEGER PRIMARY KEY,
      messagesSent INTEGER NOT NULL,
      markedSpam BOOLEAN NOT NULL,
      cooldown varchar(100),
      helpMessagesSent INTEGER NOT NULL,
-     limitLevel INTEGER
+     limitLevel INTEGER,
+     reputation INTEGER
      );
      """,
  )
```
and you would write this in [`migrate.py`](./migrate.py):
```py
import sqlite3

import schema

db = sqlite3.connect(schema.file_path)
c = db.cursor()

c.execute(
    """
    ALTER TABLE user
    ADD reputation INTEGER;
    """,
)

db.commit()
db.close()
```