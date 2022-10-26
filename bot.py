import os

import discord
from discord import option
from discord.ext import bridge
from dotenv import load_dotenv

from DeepL import get_language_list, translation
from logging_file import log
from QuillBot import quilling

load_dotenv()
TOKEN: str = os.getenv("DISCORD_TOKEN")

bot = bridge.Bot(command_prefix="g.", intents=discord.Intents.all())


@bot.event
async def on_ready() -> None:
    print(f"We have logged in as {bot.user}")


@bot.bridge_command(description="Corrects the grammar in a given text.")
@option(
    name="text",
    description="The text to be corrected.",
    required=True,
)
async def correct(ctx, *, text: str) -> None:
    message = await ctx.respond("Correcting grammar...")

    original_text = text
    corrected_text = await quilling(text)

    await message.edit_original_response(
        content=f"**__Original Text:__** {original_text}\n\n**__Corrected Text:__** {corrected_text}"
    )

    log(f"Corrected grammar for {ctx.author} in {ctx.guild}.")


####################################################################################################################


@bot.slash_command(description="Translates a given text.")
@option(
    "text",
    str,
    description="The text to translate.",
    required=True,
)
@option(
    "source_language",
    str,
    description="The language of the text.",
    required=True,
    choices=get_language_list(),
)
@option(
    "target_language",
    str,
    description="The language to translate the text to.",
    required=True,
    choices=get_language_list(),
)
@option(
    "formality_tone",
    str,
    description="The formality of the translation.",
    required=False,
    choices=["formal", "informal"],
)
async def translate(
    ctx,
    text: str,
    source_language: str,
    target_language: str,
    formality_tone: str = None,
) -> None:

    translated_text = await translation(
        text, source_language, target_language, formality_tone
    )

    await ctx.respond(
        f"**__Original Text:__** {text}\n\n**__Translated Text:__** {translated_text}"
    )

    log(f"Translated text for {ctx.author} in {ctx.guild}.")


bot.run(TOKEN)
