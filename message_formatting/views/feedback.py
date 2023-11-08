"""
Author: @sebastiaan-daniels
How to use:

from util.dev import feedback
async def my_command(ctx: discord.ApplicationContext, arg1, arg2) -> None:
    # Do stuff
    await ctx.respond("Done!", view=feedback(ctx.author, "my_command" | ctx.command.name))
"""

# Imports
import sqlite3
from time import time

import discord
import discord.ui


class feedback(discord.ui.View):
    """
    from util.dev import feedback
    async def my_command(ctx: discord.ApplicationContext, arg1, arg2) -> None:
    # Do stuff
    await ctx.respond("Done!", view=feedback(ctx.author, "my_command" | ctx.command.name))
    """

    def __init__(self, author: discord.Member, func_name: str) -> None:
        """
        ctx.author is the author of the command
        func_name is the name of the command (usually ctx.command.name)
        """
        super().__init__()
        self.author = author
        self.func_name = func_name
        self.ALLOWED_ROLES = [  # This is ok to be harcoded
            1040358438242365490,  # pax
            892124929590431815,  # VH
            267486666292199435,  # VC
            319948173554745345,  # EC
            276969339901444096,  # Staff
            639143661090766858,  # VCE
            863101381111971860,  # Subject expert
            627716753341808640,  # Retired staff
        ]

    @property
    def like_button_child(self) -> discord.ui.Button:
        assert isinstance(self.children[0], discord.ui.Button)
        return self.children[0]

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
        self.like_button_child.disabled = True
        self.dislike_button_child.disabled = True
        await self.insert(True, interaction)
        await interaction.response.edit_message(view=self)

    @property
    def dislike_button_child(self) -> discord.ui.Button:
        assert isinstance(self.children[1], discord.ui.Button)
        return self.children[1]

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
        self.like_button_child.disabled = True
        self.dislike_button_child.disabled = True
        await self.insert(False, interaction)
        await interaction.response.edit_message(view=self)

    async def insert(
        self,
        like: bool,
        interaction: discord.Interaction,
    ) -> None:
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
                getattr(interaction.message, "jump_url", "Ephemeral msg"),
            ),
        )
        db.commit()
        db.close()

    def is_allowed(self) -> bool:
        return any(role.id in self.ALLOWED_ROLES for role in self.author.roles)


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


if __name__ != "__main__":
    database()
