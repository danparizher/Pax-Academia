import os
from asyncio import Queue

import discord
from discord import option
from discord.ext import bridge
from dotenv import load_dotenv

from DeepL import get_language_list, translation
from Dictionary import (
    antonymize,
    define,
    history_and_etymology,
    phonetisize,
    synonymize,
    usage,
)
from EmbedBuilder import EmbedBuilder
from logging_file import log
from QuillBot import correcting

load_dotenv()
TOKEN: str = os.getenv("DISCORD_TOKEN")

bot = bridge.Bot(command_prefix="g.", intents=discord.Intents.all())


@bot.event
async def on_ready() -> None:
    print(f"{bot.user.name} has connected to Discord!")
    await bot.change_presence(activity=discord.Game(name="Academic Peace..."))


####################################################################################################################


def surveys() -> list[str]:
    surveys = [
        "https://forms.gle/",
        "https://docs.google.com/forms/",
        "https://www.surveymonkey.com/",
        "https://www.qualtrics.com/",
    ]
    return surveys


@bot.event
async def on_message(message: discord.Message) -> None:
    if message.channel.name != "surveys":
        for survey in surveys():
            if survey in message.content:
                embed = EmbedBuilder(
                    title="Survey Link Detected",
                    description=f"Hey {message.author.mention}, it looks like you tried to post a survey link. If this is correct, please post survey links in the <#580936851360055296> channel instead! Thanks.",
                ).build()
                await message.channel.send(embed=embed)
    await bot.process_commands(message)


####################################################################################################################


@bot.slash_command(name="define", description="Defines a word.")
async def define_command(ctx: bridge.context, word: str) -> None:

    embed = EmbedBuilder(
        title=f"Definition of __{word.capitalize()}__",
        description=f"Finding definition for {word.capitalize()}...",
    ).build()
    message = await ctx.respond(embed=embed)

    try:
        definition = define(word)
        phonetic = phonetisize(word)
        synonyms = synonymize(word)
        antonyms = antonymize(word)
        use = usage(word)
        etymology = history_and_etymology(word)
        embed = EmbedBuilder(
            title=f"Definition of __{word.capitalize()}__",
            description=definition,
            fields=[
                ("Phonetic", phonetic, False),
                ("Synonyms", synonyms, True),
                ("Antonyms", antonyms, True),
                ("First Known Use", use, False),
                ("Etymology", etymology, False),
            ],
        ).build()
        await message.edit_original_response(embed=embed)
    except Exception as e:
        embed = EmbedBuilder(
            title=f"Definition of __{word.capitalize()}__",
            description=f"Something went wrong: {e}",
        ).build()
        await message.edit_original_response(embed=embed)


####################################################################################################################


@bot.bridge_command(name="correct", description="Corrects the grammar in a given text.")
@option(
    name="text",
    description="The text to be corrected.",
    required=True,
)
async def correct(ctx, *, text: str) -> None:

    process_queue = Queue()

    await process_queue.put(ctx.author)

    embed = EmbedBuilder(
        title="Correcting Grammar",
        description=f"You are number **{process_queue.qsize()}** in the queue.",
    ).build()
    message = await ctx.respond(embed=embed)

    original_text = text
    try:
        corrected_text = await correcting(text)
    except Exception as e:
        embed = EmbedBuilder(
            title="Error",
            description=f"An error occurred while correcting the grammar:\n\n{e}",
        ).build()
        await process_queue.get()
        await message.edit_original_response(embed=embed)
        return

    embed = EmbedBuilder(
        title="Original Text",
        description=original_text,
    ).build()

    await message.edit_original_response(embed=embed)

    embed = EmbedBuilder(
        title="Corrected Text",
        description=corrected_text,
    ).build()
    await process_queue.get()
    await ctx.send(embed=embed)

    log(f"Correct command used by {ctx.author} in {ctx.guild}.")


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

    try:
        translated_text = await translation(
            text, source_language, target_language, formality_tone
        )
    except Exception as e:
        embed = EmbedBuilder(
            title="Error",
            description=f"An error occurred while translating the text:\n\n{e}",
        ).build()

        await ctx.send(embed=embed)
        return

    embed = EmbedBuilder(
        title=f"Original Text ({source_language})",
        description=f"{text}",
    ).build()

    await ctx.respond(embed=embed)

    embed = EmbedBuilder(
        title=f"Translated Text ({target_language})",
        description=f"{translated_text}",
    ).build()

    await ctx.send(embed=embed)

    log(f"Translate command used by {ctx.author} in {ctx.guild}.")


bot.run(TOKEN)
