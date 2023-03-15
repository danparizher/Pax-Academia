import sqlite3

from discord.ext import commands


class MessageCounter(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.db = sqlite3.connect("util/database.sqlite")
        self.cursor = self.db.cursor()

    @commands.Cog.listener()
    async def on_message(self, message) -> None:
        """
        It adds a user to the database if they don't exist, and updates their message count if they do

        :param message: The message object that triggered the event
        :return: The amount of messages a user has sent.
        """
        if message.author.bot:
            return

        amount = self.cursor.execute(
            "SELECT messagesSent FROM user WHERE uid = ?", (message.author.id,)
        ).fetchone()
        if amount is None:
            self.add_user(message.author.id)
        else:
            self.update_user(message.author.id, amount[0] + 1)

    def add_user(self, uid: int) -> None:
        self.cursor.execute(
            "INSERT INTO user VALUES (?, ?, ?, ?)", (uid, 1, False, None)
        )  # See ERD.mdj
        self.db.commit()

    def update_user(self, uid: int, amount: int) -> None:
        self.cursor.execute(
            "UPDATE user SET messagesSent = ? WHERE uid = ?", (amount, uid)
        )
        self.db.commit()


def setup(bot: commands.Bot) -> None:
    bot.add_cog(MessageCounter(bot))
