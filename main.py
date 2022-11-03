import asyncio
import os

import discord
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
bot = commands.Bot(command_prefix="g.", intents=discord.Intents.all())


async def load() -> None:
    for filename in os.listdir("./cogs"):
        if filename.endswith(".py"):
            bot.load_extension(f"cogs.{filename[:-3]}")


async def main() -> None:
    await load()
    await bot.start(TOKEN)


@bot.event
async def on_ready() -> None:
    print(f"{bot.user.name} has connected to Discord!")
    await bot.change_presence(activity=discord.Game(name="Academic Peace..."))


if __name__ == "__main__":
    asyncio.run(main())
