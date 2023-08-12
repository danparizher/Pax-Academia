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
        "Alerts",
        "DeepL",
        "DetectAI",
        "DetectCode",
        "Dictionary",
        "MessageCounter",
        "Misc",
        "Moderation",
        "PubChem",
        "Rules",
        "StaffAppsUser",  # v2 for users
        "StaffAppsBackoffice",  # v2 for staff
        "Surveys",
        "Tips",
        "Wikipedia",
    ]
    for cog in cogs:
        bot.load_extension(f"cogs.{cog}")


if __name__ == "__main__":
    load()
    bot.run(TOKEN)
