"""Allow to quickly check a user account for create and join time."""
#import re
import hashlib  # Used for hashing images
import discord
import time
from discord.commands import option
from discord.ext import commands

from util.EmbedBuilder import EmbedBuilder
from util.Logging import log

keeptime = 60000  # The time to keep sent messages before they are deleted in ms
recent_msgs = []  # All messages sent in the server within the last <keeptime> seconds
user_stats = {}  # The uIDs of all users who were found to be spamming or multiposting


class Staffrequirement(commands.Cog):
    """Check key account statistics of a staff applicant's account."""
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    # Allows the user to set the keeptime to a value other than the default
    @commands.slash_command(
        name="check-requirements", description="Check if the account meets requirements for staff."
    )
    @option(
        name="user ID",
        description="The uID of the account to check.",
        #autocomplete=get_keywords,
    )
    async def add_alert(self, ctx: commands.Context, userid: str) -> None:
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
        account = client.get_user(userid)  # Get the user matching the userid
        createdate = account.created_at  # The date the account was created on
        createtimestamp = account.timestamp()  # The timestamp the account was created on
        createdago = (time.time()-createdatetimestamp)/86400  # Days the account was created ago
        joindate = account.joined_at  # Joindate of the account
        log(f"User {account.mention} created on {createdate} ({createdago} ago) joined on {joindate}.")
        
        embed = EmbedBuilder(
            title="User info",
            description=f"User {account.mention} created on {createdate} ({createdago} ago) joined on {joindate}.",
        ).build()
        await ctx.respond(embed=embed, ephemeral=False)
        


def setup(bot) -> None:
    """Add the cog to the bot."""
    bot.add_cog(Staffrequirement(bot))
