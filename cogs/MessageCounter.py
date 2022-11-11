# discord imports
import discord
from discord.ext import commands

# other imports
import sqlite3

class Misc(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.db = sqlite3.connect("database.db")
        self.cursor = self.db.cursor()

    @commands.Cog.listener()
    async def on_message(self) -> None:
        ...

def setup(bot: commands.Bot) -> None:
    bot.add_cog(Misc(bot))
