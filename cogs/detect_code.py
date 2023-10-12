from __future__ import annotations

from contextlib import suppress
from itertools import islice
from os import getenv

import discord
from discord.ext import commands

import code_detection
from cogs.tips import send_tip
from message_formatting.embeds import EmbedBuilder
from util.logger import log


class DetectCode(commands.Cog):
    def __init__(self: DetectCode, bot: commands.Bot) -> None:
        self.bot = bot
        self.send_tip_in_category_id = int(
            getenv("UNFORMATTED_CODE_DETECTION_CATEGORY_ID", -1),
        )
        self.auto_format_in_channel_ids = [
            int(channel_id)
            for channel_id in getenv("AUTO_FORMAT_CODE_CHANNEL_IDS", "-1").split(",")
        ]
        print(self.auto_format_in_channel_ids)

    @staticmethod
    def format_detected_code(
        language: str,
        sections: tuple[code_detection.DetectedSection, ...],
    ) -> str:
        return "\n".join(
            f"```{language}\n{section.text}\n```" if section.is_code else section.text
            for section in sections
        )

    @staticmethod
    def get_first_lines_of_code(
        sections: tuple[code_detection.DetectedSection, ...],
        n: int = 3,
    ) -> str:
        """
        Just gets the first N lines of code from the provided sections.
        """
        code_generator = (
            line
            for section in sections
            for line in section.lines
            if section.is_code and line and not line.isspace()
        )
        return "\n".join(islice(code_generator, n))

    @staticmethod
    def likely_contains_code(text: str) -> bool:
        """
        A simple algorithm to generically detect code-like features of a message.
        """
        minimum_code_probability = 0.5

        lines = text.splitlines()

        # Most people don't paste one line of code, so this avoids false positives
        if len(lines) == 1:
            return False

        non_blank_lines = [line for line in lines if line.strip()]
        code_like_lines = [
            line
            for line in non_blank_lines
            if any(
                [
                    line.startswith("  "),
                    line.endswith((";", "{", "}", "]", "[", ")", "(", ":", ",")),
                ],
            )
        ]

        # Calculate the percentage of code-like lines
        percentage_code_like = (
            len(code_like_lines) / len(non_blank_lines) if non_blank_lines else 0
        )

        return percentage_code_like >= minimum_code_probability

    @commands.Cog.listener()
    async def on_message(self: DetectCode, message: discord.Message) -> None:
        if (
            message.author.bot
            or not isinstance(message.channel, discord.TextChannel)
            or message.channel.category is None
            or "```" in message.content
        ):
            return

        send_tips = message.channel.category.id == self.send_tip_in_category_id
        autoformat = message.channel.id in self.auto_format_in_channel_ids

        if autoformat and (detection_result := code_detection.detect(message.content)):
            language, sections = detection_result

            embed = EmbedBuilder(
                title="Auto-Formatted Code",
                description=self.format_detected_code(language, sections),
                color=0x32DC64,  # same green as tips
            ).build()

            await message.reply(
                "[How to format code on Discord?](<https://www.wikihow.com/Format-Text-as-Code-in-Discord>)",
                embed=embed,
                file=discord.File(code_detection.formatting_example_image_path),
            )

        # if language-specific algorithms fail, use a generic algorithm
        # TODO: maybe remove this once we're confident w/ our language-specific algorithms
        elif send_tips and self.likely_contains_code(message.content):
            await send_tip(message.channel, "Format Your Code", message.author, "bot")
            with suppress(AttributeError):
                log(
                    f" $ sent potential code in {message.channel.name}, bot responded with tip",
                    message.author,
                )


def setup(bot: commands.Bot) -> None:
    bot.add_cog(DetectCode(bot))
