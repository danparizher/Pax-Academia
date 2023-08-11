"""
Author: @sebastiaan-daniels
This file contains wrapper functions developers can use to
request feedback on functions that already exist in production,
but are not yet fully tested.

Users can give feedback to specific functions by liking or disliking. This will be stored in the database.
"""
# Imports
import functools
import sqlite3
import discord
import discord.ui
from time import time

ALLOWED_ROLES = [  # This is ok to be harcoded
    1040358438242365490,  # pax
    892124929590431815,  # VH
    267486666292199435,  # VC
    319948173554745345,  # EC
    410350754180890624,  # Guide
    267474828863340545  # Mod
]


class feedback(discord.ui.View):
    def __init__(self, author: discord.Member, func_name: str) -> None:
        super().__init__()
        self.author = author
        self.func_name = func_name

    @discord.ui.button(
        label="",
        style=discord.ButtonStyle.green,
        emoji="👍",
        disabled=False,
    )
    async def ok_button_callback(
        self,
        button: discord.ui.Button,
        interaction: discord.Interaction,
    ) -> None:
        if not self.is_allowed():
            await interaction.response.send_message(
                "Sorry, only Verified Helpers and above can give feedback!",
                ephemeral=True,
            )
            return
        self.children[0].disabled = True
        self.children[1].disabled = True
        await self.insert(True, interaction)
        await interaction.response.edit_message(view=self)

    @discord.ui.button(
        label="False positive",
        style=discord.ButtonStyle.red,
        emoji="👎",
        disabled=False,
    )
    async def nok_button_callback(
        self,
        button: discord.ui.Button,
        interaction: discord.Interaction,
    ) -> None:
        if not self.is_allowed():
            await interaction.response.send_message(
                "Sorry, only Verified Helpers and above can give feedback!",
                ephemeral=True,
            )
            return
        self.children[0].disabled = True
        self.children[1].disabled = True
        await self.insert(False, interaction)
        await interaction.response.edit_message(view=self)

    async def insert(self, like, interaction):
        """Inserts the feedback into the database"""
        # Since this won't be used often, we can just open and close the db every time
        db = sqlite3.connect("util/dev.sqlite")
        c = db.cursor()
        c.execute(
            "INSERT INTO feedback VALUES (?, ?, ?, ?, ?, ?)",
            (None, time(), self.author.id, self.func_name,
             like, interaction.message.jump_url),
        )
        db.commit()
        db.close()

    def is_allowed(self):
        return any([role.id in ALLOWED_ROLES for role in self.author.roles])


def database():
    """
    The database should be seperate from the production database.
    This function creates the db if it doesn't exist yet.
    An ERD is not necessary for this database.
    """
    db = sqlite3.connect("util/dev.sqlite")
    c = db.cursor()
    c.execute(
        """
        CREATE TABLE IF NOT EXISTS feedback (
            id INTEGER PRIMARY KEY,
            time TEXT NOT NULL,
            author_id INTEGER NOT NULL,
            function_name TEXT NOT NULL,
            likes INTEGER NOT NULL,
            link TEXT NOT NULL
        );
        """
    )
    db.commit()
    db.close()


def experimental(func):
    """
    USAGE:

    @experimental
    async def function():
        return tuple[discord.ApplicationContext | discord.Message, embed | content, ephemeral]

    Instead of responding to the user, return your response in a tuple.
    This wrapper will send the response and add the view.
    """
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        """
        Wrapper to add a feedback view
        """
        r = await func(*args, **kwargs)

        if r is None:
            return r

        if isinstance(r[0], discord.ApplicationContext):
            await r[0].respond(content=r[1], ephemeral=r[2], view=feedback(r[0].author, func.__name__))
        elif isinstance(r[0], discord.Message):
            await r[0].channel.send(content=r[1], view=feedback(r[0].author, func.__name__))
        return r
    return wrapper


if 'a':
    # if __name__ != "__main__":
    database()
