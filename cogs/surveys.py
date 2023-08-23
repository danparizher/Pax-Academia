from contextlib import suppress
from os import getenv

import discord
from discord.ext import commands

from message_formatting.embeds import EmbedBuilder
from util.logger import log


def survey_list() -> list[str]:
    return [
        "https://forms.gle/",
        "https://docs.google.com/forms/",
        "https://www.surveymonkey.com/",
        "https://www.qualtrics.com/",
        "https://forms.office.com/",
    ]


class Surveys(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.allow_survey_channel_id = int(
            getenv("ALLOW_SURVEY_CHANNEL_ID", -1),
        )
        self.staff_role = int(getenv("STAFF_ROLE", -1))

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message) -> None:
        """
        If the message is not in the "surveys" channel, the author does not have the "Staff" role, and
        the author is not a bot, then check if the message contains a survey link. If it does, send a
        message to the author telling them to post survey links in the "surveys" channel.

        :param message: The message object that triggered the event
        :type message: discord.Message
        """
        with suppress(AttributeError):
            if (
                message.channel.id != self.allow_survey_channel_id
                and self.staff_role not in [role.id for role in message.author.roles]
                and not message.author.bot
            ):
                for survey in survey_list():
                    if survey in message.content:
                        embed = EmbedBuilder(
                            title="Survey Link Detected",
                            description=f"Hey {message.author.mention}, it looks like you tried to post a survey link. If this is correct, please post survey links in the <#580936851360055296> channel instead! Thanks.",  # Also hardcoded channel
                        ).build()
                        with suppress(discord.errors.Forbidden):
                            await message.channel.send(
                                content=f"<@{message.author.id}>",
                                embed=embed,
                            )
                        with suppress(AttributeError):
                            log(
                                f" $ sent a survey in {message.channel.name}, bot responded",
                                message.author,
                            )
                        break
        await self.bot.process_commands(message)


def setup(bot: commands.Bot) -> None:
    bot.add_cog(Surveys(bot))
