import asyncio
import os

import discord
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
discord_intents = discord.Intents.default()
discord_intents.message_content = True
bot = commands.Bot(command_prefix="g.", intents=discord_intents)


async def load() -> None:
    cogs = [
        "DeepL",
        "MerriamWebster",
        "PubChem",
        "QuillBot",
        "Surveys",
    ]
    for cog in cogs:
        bot.load_extension(f"cogs.{cog}")


async def main() -> None:
    await load()
    await bot.start(TOKEN)


@bot.event
async def on_ready() -> None:
    print(f"{bot.user.name} has connected to Discord!")
    await bot.change_presence(activity=discord.Game(name="Academic Peace..."))


if __name__ == "__main__":
    asyncio.run(main())
