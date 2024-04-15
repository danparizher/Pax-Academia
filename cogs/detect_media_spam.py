from __future__ import annotations

from dataclasses import dataclass, field
from os import getenv
from typing import TYPE_CHECKING
from urllib.parse import urlparse

from discord.ext import commands

from message_formatting.embeds import EmbedBuilder

if TYPE_CHECKING:
    import discord
    from discord.commands.context import ApplicationContext

# How much of a channel can be media before the bot takes action.
# _Approximately_ equal to the % of vertical space on clients' screens which is occupied by media.
MAXIMUM_MEDIA_PERCENT = 2 / 3

# Up to how many messages should be considered in the media monitoring?
MEDIA_MESSAGE_LOOKBACK = 10


@dataclass
class MonitoredMessage:
    message: discord.Message

    media_vertical_pixels: int
    textual_vertical_pixels: int

    def __init__(self, message: discord.Message) -> None:
        self.message = message

        self.media_vertical_pixels = self.calculate_media_vertical_pixels(message)
        self.textual_vertical_pixels = self.calculate_textual_vertical_pixels(message)

    @staticmethod
    def extract_media_heights(message: discord.Message) -> list[int]:
        heights: list[int] = []

        # regular attachments
        heights.extend(
            att.height for att in message.attachments if att.height is not None
        )

        # embeds
        for embed in message.embeds:
            height = (embed.image and embed.image.height) or (
                embed.thumbnail and embed.thumbnail.height
            )

            # weird check for None to aid in type resolution
            if isinstance(height, int):
                heights.append(height)

        # stickers (which are always displayed 176px tall, for whatever reason)
        heights.extend((176,) * len(message.stickers))

        return heights

    @classmethod
    def calculate_media_vertical_pixels(
        cls: type[MonitoredMessage],
        message: discord.Message,
    ) -> int:
        """
        From testing, discord tends to layout multi-image posts in up to two columns
        with each row being no more than 300px tall.

        This is just an approximation - we can't perfectly replicate the client's behavior
        since every user will be using a different client (platform, resolution, etc.)
        """
        total_height = 0

        media_heights = cls.extract_media_heights(message)
        media_heights.sort()  # because media of similar height are grouped together
        for i in range(0, len(media_heights), 2):
            column_heights = media_heights[i : i + 2]
            row_height = min(max(column_heights), 300)

            total_height += row_height

        return total_height

    @staticmethod
    def calculate_textual_vertical_pixels(message: discord.Message) -> int:
        """
        All of this was measured on a 1920x1080 desktop screen at 100% zoom level, "cozy" mode.
        Includes the entire content of the message, the username, and padding/margin around the message.

        If an image/gif was embedded by URL, the URL text is not included in the calculation.
        """

        line_count = 1 + message.content.count("\n") if message.content.strip() else 0

        # check if the message content is just a link, and there is an embed from it
        # for example, when you send a tenor gif
        if any(e.type in {"image", "video", "gifv", "link"} for e in message.embeds):
            try:
                result = urlparse(message.content)
            except Exception:
                pass
            else:
                if all((result.scheme, result.netloc)):
                    # the message content is just a link
                    # so the discord client does not display it
                    line_count = 0

        return (
            18  # margin above
            + 20  # username
            + 24 * line_count  # line height
            + 8  # margin below
        )

    @property
    def mostly_media(self) -> bool:
        media = self.media_vertical_pixels
        total = media + self.textual_vertical_pixels

        return media / total > MAXIMUM_MEDIA_PERCENT


@dataclass
class ChannelMonitor:
    lookback: int = MEDIA_MESSAGE_LOOKBACK
    maximum_media_percent: float = MAXIMUM_MEDIA_PERCENT
    history: list[MonitoredMessage] = field(default_factory=list)

    def monitor(self, message: discord.Message) -> None:
        self.history.append(MonitoredMessage(message))

        while len(self.history) > self.lookback:
            del self.history[0]

    @property
    def textual_pixels(self) -> int:
        return sum(m.textual_vertical_pixels for m in self.history)

    @property
    def media_pixels(self) -> int:
        return sum(m.media_vertical_pixels for m in self.history)

    @property
    def media_percent(self) -> float:
        return self.media_pixels / (self.media_pixels + self.textual_pixels)

    @property
    def spam_detected(self) -> bool:
        # make sure that we're making a well-informed decision
        if len(self.history) < self.lookback:
            return False

        return self.media_percent > self.maximum_media_percent

    def pop_media_messages(self) -> list[discord.Message]:
        return [
            self.history.pop(i).message
            for i in range(len(self.history) - 1, -1, -1)
            if self.history[i].mostly_media
        ]


class DetectMediaSpam(commands.Cog):
    def __init__(self: DetectMediaSpam, bot: commands.Bot) -> None:
        self.bot = bot

        env_var = getenv("DETECT_MEDIA_SPAM_CHANNEL_IDS")
        self.channel_monitors_by_id = (
            {
                int(channel_id): {
                    lookback: ChannelMonitor(lookback=lookback)
                    for lookback in range(5, 26, 5)
                }
                for channel_id in env_var.split(",")
            }
            if env_var
            else {}
        )

    @commands.Cog.listener()
    async def on_message(self: DetectMediaSpam, message: discord.Message) -> None:
        channel_monitors = self.channel_monitors_by_id.get(message.channel.id)

        if not channel_monitors:
            return

        for channel_monitor in channel_monitors.values():
            channel_monitor.monitor(message)

        # TODO: delete spam if it's detected;
        #       which will be done at a later date in another PR

    @commands.slash_command(name="dev-media-statistics")
    async def dev_media_statistics(
        self: DetectMediaSpam,
        ctx: ApplicationContext,
    ) -> None:
        channel_monitors = (
            self.channel_monitors_by_id.get(ctx.channel.id) if ctx.channel else None
        )

        if not channel_monitors:
            await ctx.respond("This channel is not being monitored.", ephemeral=True)
            return

        await ctx.respond(
            embed=EmbedBuilder(
                title="Media Statistics",
                fields=[
                    field
                    for lookback, channel_monitor in channel_monitors.items()
                    for field in (
                        (
                            f"{lookback} - Media Px",
                            str(channel_monitor.media_pixels),
                            True,
                        ),
                        (
                            f"{lookback} - Text Px",
                            str(channel_monitor.textual_pixels),
                            True,
                        ),
                        (
                            f"{lookback} - Media %",
                            f"{channel_monitor.media_percent:.2%}",
                            True,
                        ),
                    )
                ],
            ).build(),
            ephemeral=True,
        )


def setup(bot: commands.Bot) -> None:
    bot.add_cog(DetectMediaSpam(bot))
