"""Allow to quickly check a user account for create and join time."""
# import re
import hashlib  # Used for hashing images
import time

import discord
from discord.commands import option
from discord.ext import commands

from util.EmbedBuilder import EmbedBuilder
from util.Logging import log


class Staffrequirement(commands.Cog):
    """Check key account statistics of a staff applicant's account."""

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    # Allows the user to set the keeptime to a value other than the default
    @commands.slash_command(
        name="check-requirements",
        description="Check if the account meets requirements for staff.",
    )
    # @option(
    #    name="user ID",
    #    description="The uID of the account to check.",
    #    #autocomplete=get_keywords,
    # )
    async def add_alert(self, ctx: commands.Context) -> None:
        """
        Allow a member of staff to check if a user meets basic criteria for becoming a staff member.

        Parameters
        ----------
        ctx : commands.Context
            DESCRIPTION.
        keyword : str
            The uID to be checked.

        Returns
        -------
        None
            DESCRIPTION.

        """
        account = ctx.author
        createdate = account.created_at  # The date the account was created on
        createtimestamp = (
            account.created_at.timestamp()
        )  # The timestamp the account was created on
        createdago = (
            time.time() - createtimestamp
        ) / 86400  # Days the account was created ago
        joindate = account.joined_at  # Joindate of the account
        log(
            f"User {account.mention} created on {createdate} ({createdago} ago) joined on {joindate}."
        )

        embed = EmbedBuilder(
            title="User info",
            description=f"{ctx.author} made a query: User {account.mention} created on {createdate} ({createdago} ago) joined on {joindate}.",
        ).build()
        await ctx.respond(embed=embed, ephemeral=True)


def setup(bot) -> None:
    """Add the cog to the bot."""
    bot.add_cog(Staffrequirement(bot))
