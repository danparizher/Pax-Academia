from datetime import datetime, timedelta
from os import getenv

import discord.ui
from discord.ext import commands

from util.EmbedBuilder import EmbedBuilder
from util.Logging import log


class StaffAppView(discord.ui.View):
    def __init__(self) -> None:
        super().__init__(timeout=None)
        self.add_item(
            discord.ui.Button(label="Apply Now", url=getenv("staff_google_form"))
        )


class StaffRequirement(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    # Allows the user to set the keeptime to a value other than the default
    @commands.slash_command(
        name="check-requirements",
        description="Check if the account meets requirements for staff.",
    )
    async def checkreqs(self, ctx: commands.Context) -> None:
        """
        It checks if the user meets the requirements to apply for staff

        :param ctx: commands.Context
        :type ctx: commands.Context
        """
        account = ctx.author

        time_since_creation = (
            datetime.now(tz=account.created_at.tzinfo) - account.created_at
        )
        time_since_join = datetime.now(tz=account.joined_at.tzinfo) - account.joined_at

        fields = [
            [
                "Created",
                f"{account.created_at.strftime('%B %d, %Y')}\n{strfdelta(time_since_creation.days/365.25,'year') if time_since_creation.days/365.25 >= 1 else ''} {strfdelta(time_since_creation.days % 365.25, 'day')} ago",
                True,
            ],
            [
                "Joined",
                f"{account.joined_at.strftime('%B %d, %Y')}\n{strfdelta(time_since_join.days/365.25, 'year') if time_since_join.days/365.25 >= 1 else ''} {strfdelta(time_since_join.days % 365.25, 'day')} ago",
                True,
            ],
        ]

        # if staff requirements are met
        # time since creation is at least 1 year (52 weeks) AND
        # time since join is at least 30 days
        if time_since_creation >= timedelta(weeks=52) and time_since_join >= timedelta(
            days=30
        ):
            embed = EmbedBuilder(
                title="Congratulations!",
                description="You meet the basic requirements for staff. You may apply for staff below.",
                fields=fields,
                color=0x39FF14,  # GREEN
            ).build()
            await ctx.respond(embed=embed, ephemeral=True, view=StaffAppView())
        else:
            embed = EmbedBuilder(
                title="Missing Requirements",
                description=f"Unfortunately, you do not meet the basic requirements in order to apply for staff.\n\nYour account must be at least 1 year old and you must have been a member of the server for at least 30 days.\n\nYou will be eligible to apply for staff in **{check_missing_requirements(time_since_creation, time_since_join)}**.",
                fields=fields,
                color=0xFF0000,  # RED
            ).build()
            await ctx.respond(embed=embed, ephemeral=True)

        log(f"User {account} checked their requirements in {ctx.guild}.")


def strfdelta(num: float, word: str) -> str:
    """
    It takes a number and a word, and returns a string that says the number and the word, with an "s" if
    the number is not 1

    :param num: The number of seconds to convert
    :type num: float
    :param word: The word to use for the time unit
    :type word: str
    :return: A string with the number of days, hours, minutes, and seconds.
    """
    return f"{num:.0f} {word}{'s' if num != 1 else ''}"


def check_missing_requirements(
    time_since_creation: timedelta, time_since_join: timedelta
) -> str:
    """
    It takes two `timedelta` objects, and returns a string of the missing requirements for the user to
    be eligible for the role

    :param time_since_creation: timedelta
    :type time_since_creation: timedelta
    :param time_since_join: timedelta = datetime.now() - member.joined_at
    :type time_since_join: timedelta
    :return: A string of the missing requirements.
    """
    missing_requirements = []
    if time_since_creation < timedelta(weeks=52):
        missing_requirements.append(
            f"{strfdelta((timedelta(weeks=52) - time_since_creation).days/365.25, 'year') if (timedelta(weeks=52) - time_since_creation).days/365.25 >= 1 else ''} {strfdelta((timedelta(weeks=52) - time_since_creation).days % 365.25, 'day')}"
        )
    if time_since_join < timedelta(days=30):
        missing_requirements.append(
            f"{strfdelta((timedelta(days=30) - time_since_join).days/365.25, 'year') if (timedelta(days=30) - time_since_join).days/365.25 >= 1 else ''} {strfdelta((timedelta(days=30) - time_since_join).days % 365.25, 'day')}"
        )
    return ", ".join(missing_requirements)


def setup(bot: commands.Bot) -> None:
    bot.add_cog(StaffRequirement(bot))
