import discord
from discord.ext import commands

from util.EmbedBuilder import EmbedBuilder


def survey_list() -> list[str]:
    surveys = [
        "https://forms.gle/",
        "https://docs.google.com/forms/",
        "https://www.surveymonkey.com/",
        "https://www.qualtrics.com/",
        "https://forms.office.com/",
    ]
    return surveys


class Surveys(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message) -> None:
        """
        If the message is not in the "surveys" channel, the author does not have the "Staff" role, and
        the author is not a bot, then check if the message contains a survey link. If it does, send a
        message to the author telling them to post survey links in the "surveys" channel.

        :param message: The message object that triggered the event
        :type message: discord.Message
        """
        try:
            if (
                message.channel.name != "surveys"
                and "276969339901444096"
                not in [role.id for role in message.author.roles]
                and not message.author.bot
            ):
                for survey in survey_list():
                    if survey in message.content:
                        embed = EmbedBuilder(
                            title="Survey Link Detected",
                            description=f"Hey {message.author.mention}, it looks like you tried to post a survey link. If this is correct, please post survey links in the <#580936851360055296> channel instead! Thanks.",
                        ).build()
                        try:
                            await message.channel.send(
                                content=f"<@{message.author.id}>", embed=embed
                            )
                        except discord.errors.Forbidden:
                            pass
        except AttributeError:
            pass
        await self.bot.process_commands(message)


def setup(bot) -> None:
    bot.add_cog(Surveys(bot))
