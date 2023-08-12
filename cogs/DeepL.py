import asyncio
from typing import Callable

import deepl
import discord
import thefuzz.process
from discord import option
from discord.ext import commands

from util.EmbedBuilder import EmbedBuilder
from util.Logging import Log, limit

# Updated 2023-08-12 based on:
# https://github.com/DeepLcom/deepl-python/blob/77f35609d665c27aa693f8e86d291dc59eb2eeaa/deepl/api_data.py#L319-L351
SOURCE_LANGUAGES = {
    "Bulgarian": "bg",
    "Czech": "cs",
    "Danish": "da",
    "German": "de",
    "Greek": "el",
    "English": "en",
    "Spanish": "es",
    "Estonian": "et",
    "Finnish": "fi",
    "French": "fr",
    "Hungarian": "hu",
    "Indonesian": "id",
    "Italian": "it",
    "Japanese": "ja",
    "Korean": "ko",
    "Lithuanian": "lt",
    "Latvian": "lv",
    "Norwegian": "nb",
    "Dutch": "nl",
    "Polish": "pl",
    "Portuguese": "pt",
    "Romanian": "ro",
    "Russian": "ru",
    "Slovak": "sk",
    "Slovenian": "sl",
    "Swedish": "sv",
    "Turkish": "tr",
    "Ukrainian": "uk",
    "Chinese": "zh",
}

TARGET_LANGUAGES = {
    "Bulgarian": "bg",
    "Czech": "cs",
    "Danish": "da",
    "German": "de",
    "Greek": "el",
    "English (British)": "en-GB",
    "English (American)": "en-US",
    "Spanish": "es",
    "Estonian": "et",
    "Finnish": "fi",
    "French": "fr",
    "Hungarian": "hu",
    "Indonesian": "id",
    "Italian": "it",
    "Japanese": "ja",
    "Korean": "ko",
    "Lithuanian": "lt",
    "Latvian": "lv",
    "Norwegian": "nb",
    "Dutch": "nl",
    "Polish": "pl",
    "Portuguese (Brazilian)": "pt-BR",
    "Portuguese (European)": "pt-PT",
    "Romanian": "ro",
    "Russian": "ru",
    "Slovak": "sk",
    "Slovenian": "sl",
    "Swedish": "sv",
    "Turkish": "tr",
    "Ukrainian": "uk",
    "Chinese": "zh",
}

FORMALITY_TONES = ["Formal", "Informal"]


def autocomplete_language(
    languages: dict[str, str]
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
    source_language: str,
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
    if source_language not in SOURCE_LANGUAGES:
        return "Invalid Source Language"

    if source_language not in TARGET_LANGUAGES:
        return "Invalid Source Language"

    if formality_tone is not None:
        if formality_tone not in FORMALITY_TONES:
            return "Invalid Formality Tone"

        # the DeepL API prefers that we use the lowercase version
        formality_tone = formality_tone.lower()

    return deepl.translate(
        text=text,
        source_language=SOURCE_LANGUAGES[source_language],
        target_language=TARGET_LANGUAGES[target_language],
        formality_tone=formality_tone,
    )


class Translation(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @commands.slash_command(name="translate", description="Translates a given text.")
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
        autocomplete=autocomplete_language(SOURCE_LANGUAGES),
    )
    @option(
        "target_language",
        str,
        description="The language to translate the text to.",
        required=True,
        autocomplete=autocomplete_language(TARGET_LANGUAGES),
    )
    @option(
        "formality_tone",
        str,
        description="The formality of the translation.",
        required=False,
        choices=FORMALITY_TONES,
    )
    @limit(2)
    async def translate(
        self,
        ctx: discord.ApplicationContext,
        text: str,
        source_language: str,
        target_language: str,
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
            title=f"Original Text ({source_language})",
            description=f"{text}",
        ).build()

        await ctx.respond(embed=embed)

        embed = EmbedBuilder(
            title=f"Translated Text ({target_language})",
            description=f"{translated_text}",
        ).build()

        await ctx.send(embed=embed)

        Log(f"Translate command used by $ in {ctx.guild}.", ctx.author)


def setup(bot: commands.Bot) -> None:
    bot.add_cog(Translation(bot))
