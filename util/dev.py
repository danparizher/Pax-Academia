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

class feedback(discord.ui.View):
    def __init__(self, author: discord.Member,) -> None:
        super().__init__()
        self.author = author
        
    @discord.ui.button(
        label="",
        style=discord.ButtonStyle.green,
        emoji="👍",
        disabled=False,
    )
    async def button_callback(
        self,
        button: discord.ui.Button,
        interaction: discord.Interaction,
    ) -> None:
        self.children[0].disabled = True
        self.children[1].disabled = True
        await interaction.response.edit_message(view=self)

    @discord.ui.button(
        label="False positive",
        style=discord.ButtonStyle.red,
        emoji="👎",
        disabled=False,
    )
    async def button_callback(
        self,
        button: discord.ui.Button,
        interaction: discord.Interaction,
    ) -> None:
        self.children[0].disabled = True
        self.children[1].disabled = True
        await interaction.response.edit_message(view=self)



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
        return tuple[ctx,embed,ephemeral]

    Instead of responding to the user, return your response in a tuple.
    This wrapper will send the response and add the view.
    """
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        """
        Wrapper to add a feedback view
        """
        r = await func(*args, **kwargs)
        await r[0].respond(content=r[1], ephemeral=r[2], view=feedback(r[0].author))
        return r
    return wrapper


if 'a':
#if __name__ != "__main__":
    database()