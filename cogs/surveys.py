from contextlib import suppress
from os import getenv

import discord
from discord.ext import commands

from message_formatting.embeds import EmbedBuilder
from util.logger import log

SURVEY_SITES = [
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
        if not isinstance(message.author, discord.Member):
            return

        if message.author.bot:
            # bots are allowed to post surveys
            return

        if self.staff_role in (role.id for role in message.author.roles):
            # staff are allowed to post surveys
            return

        if message.channel.id == self.allow_survey_channel_id:
            # surveys are allowed to be posted in #surveys
            return

        if all(survey_site not in message.content for survey_site in SURVEY_SITES):
            # message does not contain a survey link
            return

        embed = EmbedBuilder(
            title="Survey Link Detected",
            description=(
                f"Hey {message.author.mention}, it looks like you tried to post a survey link."
                f" If this is correct, please post survey links in the"
                f" <#{self.allow_survey_channel_id}> channel instead! Thanks."
            ),
        ).build()

        with suppress(discord.errors.Forbidden):
            await message.channel.send(
                content=f"<@{message.author.id}>",
                embed=embed,
            )

        channel_name = getattr(message.channel, "name", f"<#{message.channel.id}>")
        log(
            f" $ sent a survey in {channel_name}, bot responded",
            message.author,
        )


def setup(bot: commands.Bot) -> None:
    bot.add_cog(Surveys(bot))
