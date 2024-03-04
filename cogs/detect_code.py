from __future__ import annotations

import re

import asyncio
from contextlib import suppress
from itertools import islice
from os import getenv
from typing import ClassVar

import discord
from discord.ext import commands

import code_detection
from cogs.tips import send_tip
from message_formatting.embeds import EmbedBuilder
from util.logger import log


class DetectCode(commands.Cog):
    # maps (channel id, message id) -> message
    # for all tip messages sent in the last hour
    # (useful so that we can delete the tip if they fix their message)
    sent_tip_messages: ClassVar[dict[tuple[int, int], discord.Message]] = {}

    def __init__(self: DetectCode, bot: commands.Bot) -> None:
        self.bot = bot
        self.send_tip_in_category_id = int(
            getenv("UNFORMATTED_CODE_DETECTION_CATEGORY_ID", -1),
        )
        self.auto_format_in_channel_ids = [
            int(channel_id)
            for channel_id in getenv("AUTO_FORMAT_CODE_CHANNEL_IDS", "-1").split(",")
        ]

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

        # Most people don't have less than around 5 lines of code, so we can ignore them
        if len(lines) < 5:
            return False

        non_blank_lines = [line for line in lines if line.strip()]

        patterns = [
            r"\w+\s*\(.*\)",
            r"#",
            r"'''",
            r'"""',
            r";(?=\s*(//|#).+|$)",
            r"^\w+(\.\w+)+$",
            r"\w+(->\w+)+",
            r"^\/\*",
            r"\*/$",
            r"[a-z][A-Z]",
            r"^\w+(?:_\w+)+$",
            r"\b[a-zA-Z0-9]+(?:-[a-zA-Z0-9]+)+\b",
        ]

        code_like_lines = [
            line
            for line in non_blank_lines
            if any(re.search(line, pattern) for pattern in patterns)
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

            tip_message = await message.reply(
                "[How to format code on Discord?](<https://www.wikihow.com/Format-Text-as-Code-in-Discord>)",
                embed=embed,
                file=discord.File(code_detection.formatting_example_image_path),
            )

        # if language-specific algorithms fail, use a generic algorithm
        # TODO: maybe remove this once we're confident w/ our language-specific algorithms
        elif send_tips and self.likely_contains_code(message.content):
            tip_message = await send_tip(
                message.channel,
                "Format Your Code",
                message.author,
                "bot",
            )
            assert isinstance(
                tip_message,
                discord.Message,
            ), "channel.send() always returns `Message`s"

            with suppress(AttributeError):
                log(
                    f" $ sent potential code in {message.channel.name}, bot responded with tip",
                    message.author,
                )
        else:
            return

        # keep record of this tip being sent for 1 hour
        uuid = (message.channel.id, message.id)
        self.sent_tip_messages[uuid] = tip_message
        await asyncio.sleep(60 * 60)
        with suppress(KeyError):
            del self.sent_tip_messages[uuid]

    @commands.Cog.listener()
    async def on_raw_message_delete(
        self: DetectCode,
        payload: discord.RawMessageDeleteEvent,
    ) -> None:
        uuid = (payload.channel_id, payload.message_id)
        if sent_tip_message := self.sent_tip_messages.pop(uuid, None):
            await sent_tip_message.delete()

    @commands.Cog.listener()
    async def on_raw_message_edit(
        self: DetectCode,
        payload: discord.RawMessageUpdateEvent,
    ) -> None:
        changes = dict(payload.data)
        if not isinstance(new_content := changes.get("content"), str):
            return

        if "```" in new_content:
            uuid = (payload.channel_id, payload.message_id)
            if sent_tip_message := self.sent_tip_messages.pop(uuid, None):
                await sent_tip_message.delete()


def setup(bot: commands.Bot) -> None:
    bot.add_cog(DetectCode(bot))
