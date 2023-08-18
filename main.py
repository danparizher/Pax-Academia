import os

import discord
from discord.ext import commands
from dotenv import load_dotenv

# Creates the db if it doesn't exist
import util.db_builder

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
discord_intents = discord.Intents.default()
discord_intents.message_content = True
bot = commands.Bot(command_prefix="g.", intents=discord_intents)


def load() -> None:
    cogs = [
        "alerts",
        #"deepl",
        "detect_ai",
        "detect_code",
        "dictionary",
        "message_counter",
        "misc",
        "moderation",
        "pubchem",
        "rules",
        "staffapps_frontend",  # v2 for users
        "staffapps_backend",  # v2 for staff
        "surveys",
        "tips",
        "wikipedia",
    ]
    for cog in cogs:
        bot.load_extension(f"cogs.{cog}")


if __name__ == "__main__":
    load()
    bot.run(TOKEN)
