from __future__ import annotations

import discord
from discord.ext import commands

import database


class MessageCounter(commands.Cog):
    def __init__(self: MessageCounter, bot: commands.Bot) -> None:
        self.bot = bot
        self.db = database.connect()
        self.cursor = self.db.cursor()

    @commands.Cog.listener()
    async def on_message(self: MessageCounter, message: discord.Message) -> None:
        """
        It adds a user to the database if they don't exist, and updates their message count if they do

        :param message: The message object that triggered the event
        :return: The amount of messages a user has sent.
        """

        # Ignore messages from bots
        if message.author.bot:
            return

        if isinstance(message.channel, discord.DMChannel):
            return

        messages_sent = (
            None
            if (
                sent := self.cursor.execute(
                    "SELECT messagesSent, helpMessagesSent FROM user WHERE uid = ?",
                    (message.author.id,),
                ).fetchall()
            )
            == []
            else sent
        )

        # If a user is not in db, add them
        if messages_sent is None:
            self.add_user(message.author.id)
            messages_sent = (0, 0)
        else:
            messages_sent = messages_sent[0]

        # If the message was sent in a help channel, update the helpMessagesSent column
        category = getattr(message.channel, "category", None)
        if category and "help" in category.name:
            self.update_help_user(message.author.id, messages_sent[1] + 1)

        # Update the messagesSent column
        self.update_user(message.author.id, messages_sent[0] + 1)

        # commit changes
        self.db.commit()

    def add_user(self: MessageCounter, uid: int) -> None:
        self.cursor.execute(
            "INSERT INTO user VALUES (?, ?, ?, ?, ?, ?)",
            (uid, 0, False, None, 0, None),
        )  # See ERD.mdj

    def update_user(self: MessageCounter, uid: int, amount: int) -> None:
        self.cursor.execute(
            "UPDATE user SET messagesSent = ? WHERE uid = ?",
            (amount, uid),
        )

    def update_help_user(self: MessageCounter, uid: int, amount: int) -> None:
        self.cursor.execute(
            "UPDATE user SET helpMessagesSent = ? WHERE uid = ?",
            (amount, uid),
        )


def setup(bot: commands.Bot) -> None:
    bot.add_cog(MessageCounter(bot))
