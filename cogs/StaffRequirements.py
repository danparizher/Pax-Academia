from datetime import datetime

from discord.ext import commands

from util.EmbedBuilder import EmbedBuilder
from util.Logging import log


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
        created_years_ago = (
            datetime.now(tz=account.created_at.tzinfo) - account.created_at
        ).days // 365
        created_days_ago = (
            datetime.now(tz=account.created_at.tzinfo) - account.created_at
        ).days % 365

        joined_years_ago = (
            datetime.now(tz=account.joined_at.tzinfo) - account.joined_at
        ).days // 365
        joined_days_ago = (
            datetime.now(tz=account.joined_at.tzinfo) - account.joined_at
        ).days % 365
        
        content=[
            [
                "Account Age",
                f"**{created_years_ago}** year{'s' if created_years_ago != 1 else ''}, **{created_days_ago}** day{'s' if created_days_ago != 1 else ''}",
                True,
            ],
            [
                "Joined",
                f"**{joined_years_ago}** year{'s' if joined_years_ago != 1 else ''}, **{joined_days_ago}** day{'s' if joined_days_ago != 1 else ''} ago",
                True,
            ]
        ]
        if (created_years_ago >= 1) and (joined_days_ago >= 30):
            content.append([
                f"Congratulations, {account.mention}! You meet the basic requirements for staff. Please fill out the application form [here](https://goo.gl/forms/Z3mVQwLdiNZcKHx52)."
                ])
        else:
            content.append([
                f"Unfortunately, you do not meet the basic requirements in order to apply for staff. Your account must be at least 1 year old and you must have been a member of the server for at least 30 days."
                ])
        embed = EmbedBuilder(
            title="User info",
            description=f"{account.mention} was created on {account.created_at.strftime('%B %d, %Y')} and joined on {account.joined_at.strftime('%B %d, %Y')}.",
            fields=content,
        ).build()
        await ctx.respond(embed=embed, ephemeral=True)

        log(f"User {account} checked their requirements in {ctx.guild}.")


def setup(bot) -> None:
    bot.add_cog(StaffRequirement(bot))
