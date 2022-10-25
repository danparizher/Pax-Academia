import os

import discord
from discord.ext import bridge
from dotenv import load_dotenv

from logging_file import log
from webcache import quilling

load_dotenv()
TOKEN: str = os.getenv("DISCORD_TOKEN")

bot = bridge.Bot(command_prefix="g.", intents=discord.Intents.all())


@bot.event
async def on_ready() -> None:
    print(f"We have logged in as {bot.user}")


@bot.bridge_command(description="Corrects the grammar in a given text.")
async def correct(ctx, *, text: str) -> None:
    message = await ctx.respond("Correcting grammar...")

    original_text = text
    corrected_text = await quilling(text)

    await message.edit_original_response(
        content=f"**__Original Text:__** {original_text}\n\n**__Corrected Text:__** {corrected_text}"
    )

    log(f"Corrected grammar for {ctx.author} in {ctx.guild}.")


bot.run(TOKEN)
