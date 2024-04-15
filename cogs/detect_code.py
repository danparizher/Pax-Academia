from __future__ import annotations

import asyncio
from contextlib import suppress
from os import getenv
from typing import ClassVar

import discord
from discord.ext import commands

import code_detection
from message_formatting.embeds import EmbedBuilder


class DetectCode(commands.Cog):
    # maps (channel id, message id) -> message
    # for all tip messages sent in the last hour
    # (useful so that we can delete the tip if they fix their message)
    sent_tip_messages: ClassVar[dict[tuple[int, int], discord.Message]] = {}

    def __init__(self: DetectCode, bot: commands.Bot) -> None:
        self.bot = bot
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

    @commands.Cog.listener()
    async def on_message(self: DetectCode, message: discord.Message) -> None:
        if (
            message.author.bot
            or not isinstance(message.channel, discord.TextChannel)
            or "```" in message.content
        ):
            return

        autoformat = message.channel.id in self.auto_format_in_channel_ids

        if not autoformat:
            return

        detection_result = code_detection.detect(message.content)
        if not detection_result:
            return

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
