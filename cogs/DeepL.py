import asyncio

import deepl
import discord
import thefuzz.process
from discord import option
from discord.ext import commands

from util.EmbedBuilder import EmbedBuilder
from util.Logging import Log, limit

LANGUAGES = [
    "Bulgarian",
    "Chinese",
    "Czech",
    "Danish",
    "Dutch",
    "English",
    "Estonian",
    "Finnish",
    "French",
    "German",
    "Greek",
    "Hungarian",
    "Indonesian",
    "Italian",
    "Japanese",
    "Korean",
    "Latvian",
    "Lithuanian",
    "Norwegian",
    "Polish",
    "Portuguese",
    "Romanian",
    "Russian",
    "Slovak",
    "Slovenian",
    "Spanish",
    "Swedish",
    "Turkish",
    "Ukrainian",
]
FORMALITY_TONES = ["Formal", "Informal"]


def autocomplete_language(ctx: discord.AutocompleteContext) -> list[str]:
    current = ctx.value
    if not current.strip():
        return LANGUAGES[:25]
    else:
        matches: list[tuple[str, int]]
        matches = thefuzz.process.extract(current, LANGUAGES, limit=25)  # type: ignore

        minimum_score = matches[0][1] / 2

        return [language for language, score in matches if score > minimum_score]


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
    if source_language not in LANGUAGES or target_language not in LANGUAGES:
        return "Invalid Language"

    if formality_tone is not None:
        if formality_tone not in FORMALITY_TONES:
            return "Invalid Formality Tone"

        # the DeepL API prefers that we use the lowercase version
        formality_tone = formality_tone.lower()

    return deepl.translate(
        text=text,
        source_language=source_language,
        target_language=target_language,
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
        autocomplete=autocomplete_language,
    )
    @option(
        "target_language",
        str,
        description="The language to translate the text to.",
        required=True,
        autocomplete=autocomplete_language,
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
        ctx: commands.Context,
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

            await ctx.send(embed=embed, ephemeral=True)
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


# TODO(<@pharmony_01>): Create an autocomplete for the languages so that the user isn't limited to the first 25 languages
# https://github.com/Arborym/Pax-Academia/issues/194
def setup(bot: commands.Bot) -> None:
    bot.add_cog(Translation(bot))
