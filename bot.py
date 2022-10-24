import os

import discord
from discord.ext import bridge
from dotenv import load_dotenv

from webcache import quilling
from logging import log

load_dotenv()
TOKEN: str = os.getenv("DISCORD_TOKEN")

bot = bridge.Bot(command_prefix="g.", intents=discord.Intents.all())


@bot.event
async def on_ready() -> None:
    print(f"We have logged in as {bot.user}")


@bot.bridge_command()
async def correct(ctx, text: str) -> None:
    await ctx.respond("Correcting grammar...")
    corrected_text: str = await quilling(text)
    await ctx.respond(corrected_text)
    log(f"Corrected grammar for {ctx.author} in {ctx.guild}.")


bot.run(TOKEN)
