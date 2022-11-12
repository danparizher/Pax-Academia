"""Allow to quickly check a user account for create and join time."""
# import re
import time
from datetime import datetime

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
        # createdate = account.created_at  # The date the account was created on
        createtimestamp = (
            account.created_at.timestamp()
        )  # The timestamp the account was created on

        timediff = time.time() - createtimestamp
        created_years_ago = timediff // 31536000  # Years the account was created ago
        created_days_ago = int((timediff - 31536000 * created_years_ago) / 86400)

        joindate = account.joined_at.timestamp()  # Joindate of the account
        timediff = time.time() - joindate
        joined_days_ago = int(timediff / 86400)
        
        log(
            f"{ctx.author} made a query: User {account.mention} created on {datetime.fromtimestamp(createtimestamp).strftime('%A, %B %d, %Y %I:%M:%S')} ({created_years_ago} years, {created_days_ago} days ago) joined on {datetime.fromtimestamp(joindate).strftime('%A, %B %d, %Y %I:%M:%S')}."
        )

        embed = EmbedBuilder(
            title="User info",
            description=f"User {account.mention} created on {datetime.fromtimestamp(createtimestamp).strftime('%A, %B %d, %Y %I:%M:%S')} ({created_years_ago} year{'s' if created_years_ago != 1 else ''}, {created_days_ago} days ago) joined on {datetime.fromtimestamp(joindate).strftime('%A, %B %d, %Y %I:%M:%S')}.",
        ).build()
        await ctx.respond(embed=embed, ephemeral=True)
        
        if (created_years_ago >= 1) and (joined_days_ago >= 30) :
            embed = EmbedBuilder(
                title="Application Link",
                description=f"Congratulations, you meet the basic requirements in order to apply for staff. Please visit https://goo.gl/forms/Z3mVQwLdiNZcKHx52 for the next step. Please note that this is not a guarantee that you will be accepted."
            ).build()
            await ctx.respond(embed=embed, ephemeral=True)
        else:
            embed = EmbedBuilder(
                title="Missing Requirements",
                description=f"Unfortunately your account does not meet the basic requirements to allow you to apply for staff. You need to be a server member for at least 30 days and your account must be at least one year old."
            ).build()
            await ctx.respond(embed=embed, ephemeral=True)


def setup(bot) -> None:
    """Add the cog to the bot."""
    bot.add_cog(Staffrequirement(bot))
