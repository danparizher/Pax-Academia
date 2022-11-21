from datetime import datetime, timedelta

import discord.ui
from discord.ext import commands

from util.EmbedBuilder import EmbedBuilder
from util.Logging import log
from os import getenv

class StaffAppView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(discord.ui.Button(label="Apply Now", url=getenv('staff_google_form')))

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

        time_since_creation = datetime.now(tz=account.created_at.tzinfo) - account.created_at
        time_since_join = datetime.now(tz=account.joined_at.tzinfo) - account.joined_at

        fields=[
            [
                "Created",
                f"{account.created_at.strftime('%B %d, %Y')}\n{strfdelta(time_since_creation.days/365.25,'year')}, {strfdelta(time_since_creation.days % 365.25, 'day')} ago",
                True
            ],
            [
                "Joined",
                f"{account.joined_at.strftime('%B %d, %Y')}\n{strfdelta(time_since_join.days/365.25, 'year')}, {strfdelta(time_since_join.days % 365.25, 'day')} ago",
                True
            ]
        ]

        # if staff requirements are met
        # time since creation is at least 1 year (52 weeks) AND
        # time since join is at least 30 days
        if time_since_creation >= timedelta(weeks=52) and time_since_join >= timedelta(days=30):
            embed = EmbedBuilder(
                title="Congratulations!",
                description="You meet the basic requirements for staff. You may apply for staff below.",
                fields=fields,
                color=0x39ff14 # GREEN
            ).build()
            await ctx.respond(embed=embed, ephemeral=True, view=StaffAppView())
        else:
            embed = EmbedBuilder(
                title="Missing Requirements",
                description=f"Unfortunately, you do not meet the basic requirements in order to apply for staff. Your account must be at least 1 year old and you must have been a member of the server for at least 30 days.",
                fields=fields,
                color=0xff0000 # RED
            ).build()
            await ctx.respond(embed=embed, ephemeral=True)

        log(f"User {account} checked their requirements in {ctx.guild}.")

def strfdelta(num: float, word: str) -> str:
    rounded_num = round(num)
    return f"{rounded_num} {word if rounded_num == 1 else word + 's'}"

def setup(bot) -> None:
    bot.add_cog(StaffRequirement(bot))
