import os
import re

import discord
from discord import option
from discord.ext import bridge
from dotenv import load_dotenv

from DeepL import get_language_list, translation
from EmbedBuilder import EmbedBuilder
from logging_file import log
from QuillBot import quilling

load_dotenv()
TOKEN: str = os.getenv("DISCORD_TOKEN")

bot = bridge.Bot(command_prefix="g.", intents=discord.Intents.all())


@bot.event
async def on_ready() -> None:
    print(f"{bot.user.name} has connected to Discord!")
    await bot.change_presence(activity=discord.Game(name="Academic Peace..."))


####################################################################################################################


@bot.event
async def on_message(message: discord.Message) -> None:
    if re.search(r"https?://", message.content):
        if re.search(r"form|qualtric|survey", message.content):
            if message.channel.name != "surveys":
                embed = EmbedBuilder(
                    title="Survey Link Detected",
                    description=f"Hey {message.author.mention}, it looks like you tried to post a survey link. Please post survey links in the #surveys channel! Thanks.",
                ).build()
                await message.channel.send(embed=embed)
    await bot.process_commands(message)


####################################################################################################################


@bot.bridge_command(name="correct", description="Corrects the grammar in a given text.")
@option(
    name="text",
    description="The text to be corrected.",
    required=True,
)
async def correct(ctx, *, text: str) -> None:

    message = await ctx.respond("Correcting grammar...")

    original_text = text
    corrected_text = await quilling(text)

    embed = EmbedBuilder(
        title="Grammar Correction",
        description=f"**__Original Text:__**\n{original_text}\n\n**__Corrected Text:__**\n{corrected_text}",
    ).build()

    await message.edit_original_response(embed=embed)

    log(f"Corrected grammar for {ctx.author} in {ctx.guild}.")


####################################################################################################################


@bot.slash_command(name="translate", description="Translates a given text.")
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
    choices=["Formal", "Informal"],
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

    embed = EmbedBuilder(
        title="Translation",
        description=f"**__Original Text ({source_language}):__**\n{text}\n\n**__Translated Text ({target_language}):__**\n{translated_text}",
    ).build()

    await ctx.respond(embed=embed)

    log(f"Translated text for {ctx.author} in {ctx.guild}.")


bot.run(TOKEN)
