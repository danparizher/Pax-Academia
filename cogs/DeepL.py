from deepl import translate
from discord import option
from discord.ext import commands

from globalfuncs.EmbedBuilder import EmbedBuilder
from globalfuncs.Logging import log


def get_language_list() -> list[str]:
    languages = [
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
        "Italian",
        "Japanese",
        "Latvian",
        "Lithuanian",
        "Polish",
        "Portuguese",
        "Romanian",
        "Russian",
        "Slovak",
        "Slovenian",
        "Spanish",
        "Swedish",
    ]
    return languages


async def translation(
    text, source_language, target_language, formality_tone=None
) -> str:

    formality = ["formal", "informal"]
    languages = get_language_list()

    if source_language not in languages or target_language not in languages:
        return "Invalid Language"

    if formality_tone is not None:
        formality_tone = formality_tone.lower()

    if formality_tone is not None and formality_tone not in formality:
        return "Invalid Formality"

    return translate(
        text=text,
        source_language=source_language,
        target_language=target_language,
        formality_tone=formality_tone,
    )


class Translation(commands.Cog):
    def __init__(self, bot) -> None:
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
        self,
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


def setup(bot) -> None:
    bot.add_cog(Translation(bot))
