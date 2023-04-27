import sqlite3

from discord.ext import commands


class MessageCounter(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.db = sqlite3.connect("util/database.sqlite")
        self.cursor = self.db.cursor()

    @commands.Cog.listener()
    async def on_message(self, message: commands.Context) -> None:
        """
        It adds a user to the database if they don't exist, and updates their message count if they do

        :param message: The message object that triggered the event
        :return: The amount of messages a user has sent.
        """

        # Ignore messages from bots
        if message.author.bot:
            return

        messages_sent = None if (sent := self.cursor.execute(
            "SELECT messagesSent, helpMessagesSent FROM user WHERE uid = ?",
            (message.author.id,),
        ).fetchall()) == [] else sent

        # Fetch the category name of the channel the message was sent in
        category_name = message.channel.category.name.lower()

        # If a user is not in db, add them
        if messages_sent is None:
            self.add_user(message.author.id)
            messages_sent = (0, 0)
        else:
            messages_sent = messages_sent[0]

        # If the message was sent in a help channel, update the helpMessagesSent column
        if "help" in category_name:
            self.update_help_user(message.author.id, messages_sent[1] + 1)

        # Update the messagesSent column
        self.update_user(message.author.id, messages_sent[0] + 1)

        # commit changes
        self.db.commit()


    def add_user(self, uid: int) -> None:
        self.cursor.execute(
            "INSERT INTO user VALUES (?, ?, ?, ?, ?)",
            (uid, 0, False, None, 0),
        )  # See ERD.mdj

    def update_user(self, uid: int, amount: int) -> None:
        self.cursor.execute(
            "UPDATE user SET messagesSent = ? WHERE uid = ?",
            (amount, uid),
        )

    def update_help_user(self, uid: int, amount: int) -> None:
        self.cursor.execute(
            "UPDATE user SET helpMessagesSent = ? WHERE uid = ?",
            (amount, uid),
        )


def setup(bot: commands.Bot) -> None:
    bot.add_cog(MessageCounter(bot))
