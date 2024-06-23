from __future__ import annotations

import asyncio
from os import getenv
from typing import Callable

import deepl
import discord
import thefuzz.process
from discord import option
from discord.ext import commands

from message_formatting.embeds import EmbedBuilder
from util.limiter import limit
from util.logger import log

# Note to developers:
# If you get an error here, it's probably because
# you don't have a DeepL API key in your `.env`.
# If you don't want to create a DeepL account, you can just
# disable the cog by commenting it out in main.py
translator = deepl.Translator(getenv("DEEPL_API_KEY", ""))
SOURCE_LANGUAGES = {l.name: l for l in translator.get_source_languages()}
TARGET_LANGUAGES = {l.name: l for l in translator.get_target_languages()}
FORMALITY_TONES = {f.value.replace("_", " ").title(): f.value for f in deepl.Formality}


def autocomplete_language(
    languages: dict[str, deepl.Language],
) -> Callable[[discord.AutocompleteContext], list[str]]:
    language_names = list(languages.keys())

    def autocomplete(ctx: discord.AutocompleteContext) -> list[str]:
        current = ctx.value
        if not current.strip():
            return language_names[:25]
        matches: list[tuple[str, int]]
        matches = thefuzz.process.extract(current, language_names, limit=25)  # type: ignore
        highest_score = matches[0][1]

        return [language for language, score in matches if score > highest_score / 2]

    return autocomplete


def translate(
    text: str,
    source_language: str | None,
    target_language: str,
    formality_tone: str | None = None,
) -> str:
    """
    We use the `deepl.translate` function to translate the text, but we do it in a separate thread so
    that we can asynchronously wait for it to be completed

    :param text: The text to translate
    :type text: str
    :param source_language: The language that the text is currently in
    :type source_language: str
    :param target_language: The language you want to translate to
    :type target_language: str
    :param formality_tone: The formality tone of the translation
    :type formality_tone: Optional[str]
    :return: The translated text.
    """
    if source_language and source_language not in SOURCE_LANGUAGES:
        msg = "Invalid Source Language"
        raise ValueError(msg)

    if target_language not in TARGET_LANGUAGES:
        msg = "Invalid Target Language"
        raise ValueError(msg)

    if formality_tone:
        if formality_tone not in FORMALITY_TONES:
            msg = "Invalid Formality Tone"
            raise ValueError(msg)

        if not TARGET_LANGUAGES[target_language].supports_formality:
            msg = f"{target_language} formality tones are not supported!"
            raise ValueError(msg)

    result = translator.translate_text(
        text,
        source_lang=SOURCE_LANGUAGES[source_language] if source_language else None,
        target_lang=TARGET_LANGUAGES[target_language],
        formality=FORMALITY_TONES[formality_tone] if formality_tone else None,
    )

    if isinstance(result, list):
        return "\n".join(line.text for line in result)
    return result.text


class Translation(commands.Cog):
    def __init__(self: Translation, bot: commands.Bot) -> None:
        self.bot = bot

    @commands.slash_command(name="translate", description="Translates a given text.")
    @option(
        "text",
        str,
        description="The text to translate.",
        required=True,
    )
    @option(
        "target_language",
        str,
        description="The language to translate the text to.",
        required=True,
        autocomplete=autocomplete_language(TARGET_LANGUAGES),
    )
    @option(
        "source_language",
        str,
        description="The language of the text.",
        required=False,  # default = auto-detect
        autocomplete=autocomplete_language(SOURCE_LANGUAGES),
    )
    @option(
        "formality_tone",
        str,
        description="The formality of the translation.",
        required=False,
        choices=FORMALITY_TONES.keys(),
    )
    @limit(2)
    async def translate(
        self: Translation,
        ctx: discord.ApplicationContext,
        text: str,
        target_language: str,
        source_language: str | None = None,
        formality_tone: str | None = None,
    ) -> None:
        """
        It translates text from one language to another

        :param ctx: The context of the command
        :param text: The text to translate
        :type text: str
        :param source_language: The language the text is in
        :type source_language: str
        :param target_language: str = "en"
        :type target_language: str
        :param formality_tone: Optional[str] = None
        :type formality_tone: Optional[str]
        :return: The translated text.
        """
        if source_language == target_language:
            embed = EmbedBuilder(
                title="Error",
                description="Source language and target language cannot be the same.",
            ).build()

            await ctx.respond(embed=embed, ephemeral=True)
            return
        try:
            translated_text = await asyncio.to_thread(
                translate,
                text,
                source_language,
                target_language,
                formality_tone,
            )
        except Exception as e:
            embed = EmbedBuilder(
                title="Error",
                description=f"An error occurred while translating the text:\n\n{e}",
            ).build()

            await ctx.respond(embed=embed, ephemeral=True)
            return

        embed = EmbedBuilder(
            title=f"Original Text - {source_language or 'Auto Detect'}",
            description=text,
        ).build()

        await ctx.respond(embed=embed)

        embed = EmbedBuilder(
            title=f"Translated Text - {target_language}",
            description=translated_text,
        ).build()

        await ctx.send(embed=embed)

        log(f"Translate command used by $ in {ctx.guild}.", ctx.author)


def setup(bot: commands.Bot) -> None:
    bot.add_cog(Translation(bot))
