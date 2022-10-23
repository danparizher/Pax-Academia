import os

import discord
from dotenv import load_dotenv

from webcache import main

load_dotenv()
TOKEN: str | None = os.getenv("DISCORD_TOKEN")

bot = discord.Bot()


@bot.event
async def on_ready():
    print(f"We have logged in as {bot.user}")


@bot.slash_command(guild_ids=[883845473893482517])
async def hello(ctx):
    await ctx.respond("Hello!")


bot.run(TOKEN)
