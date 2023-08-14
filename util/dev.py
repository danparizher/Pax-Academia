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
from collections.abc import Coroutine
from time import time
from typing import Any

import discord
import discord.ui

ALLOWED_ROLES = [  # This is ok to be harcoded
    1040358438242365490,  # pax
    892124929590431815,  # VH
    267486666292199435,  # VC
    319948173554745345,  # EC
    276969339901444096,  # Staff
    639143661090766858,  # VCE
    863101381111971860,  # Subject expert
    627716753341808640,  # Retired staff
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

    async def insert(
        self,
        like: bool,
        interaction: discord.Interaction,
    ) -> Coroutine[Any, Any, None]:
        """Inserts the feedback into the database"""
        # Since this won't be used often, we can just open and close the db every time
        db = sqlite3.connect("util/dev.sqlite")
        c = db.cursor()
        c.execute(
            "INSERT INTO feedback VALUES (?, ?, ?, ?, ?, ?)",
            (
                None,
                time(),
                self.author.id,
                self.func_name,
                like,
                interaction.message.jump_url,
            ),
        )
        db.commit()
        db.close()

    def is_allowed(self) -> bool:
        return any(role.id in ALLOWED_ROLES for role in self.author.roles)


def database() -> None:
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
        """,
    )
    db.commit()
    db.close()


def experimental(func: Coroutine) -> Coroutine:
    """
    USAGE:

    @experimental
    async def function():
        return tuple[discord.ApplicationContext | discord.Message, embed | content, ephemeral]

    Instead of responding to the user, return your response in a tuple.
    This wrapper will send the response and add the view.
    """

    @functools.wraps(func)
    async def wrapper(*args, **kwargs) -> Coroutine[Any, Any, None]:
        """
        Wrapper to add a feedback view
        """
        r = await func(*args, **kwargs)

        if r is None:
            return r

        if isinstance(r[0], discord.ApplicationContext):
            await r[0].respond(
                content=r[1],
                ephemeral=r[2],
                view=feedback(r[0].author, func.__name__),
            )
        elif isinstance(r[0], discord.Message):
            await r[0].channel.send(
                content=r[1],
                view=feedback(r[0].author, func.__name__),
            )
        return r

    return wrapper


if __name__ != "__main__":
    database()