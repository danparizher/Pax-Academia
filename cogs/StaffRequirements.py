from datetime import datetime, timedelta
from os import getenv

import discord.ui
from discord.ext import commands
from humanize import precisedelta

import sqlite3

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
        self.db= sqlite3.connect("util/database.sqlite")
        self.cursor = self.db.cursor()

    def fetch_message_count(self, uid):
        self.cursor.execute("SELECT amount FROM messagecount WHERE uid = ?", (uid,))
        return self.cursor.fetchone()[0]

    # Allows the user to set the keeptime to a value other than the default
    @commands.slash_command(
        name="apply-for-staff",
        description="Apply for a staff position if your account meets the requirements!",
    )
    async def checkreqs(self, ctx: commands.Context) -> None:
        """
        It checks if the user meets the requirements to apply for staff

        :param ctx: commands.Context
        :type ctx: commands.Context
        """
        msg_amount = self.fetch_message_count(ctx.author.id)
        account = ctx.author

        time_since_creation = (
            datetime.now(tz=account.created_at.tzinfo) - account.created_at
        )
        time_since_join = datetime.now(tz=account.joined_at.tzinfo) - account.joined_at

        fields = [
            [
                "Created",
                f"""{account.created_at.strftime('%B %d, %Y')}
                {precisedelta(time_since_creation, minimum_unit='days', format="%.0F")} ago""",
                True,
            ],
            [
                "Joined",
                f"""{account.joined_at.strftime('%B %d, %Y')}
                {precisedelta(time_since_join, minimum_unit='days', format="%.0F")} ago""",
                True,
            ],
            [
                "Messages",
                f"{msg_amount} messages",
                True
            ]
        ]

        # if staff requirements are met
        # time since creation is at least 1 year (52 weeks) AND
        # time since join is at least 30 days
        if time_since_creation >= timedelta(weeks=52) and time_since_join >= timedelta(
            days=30
        ) and msg_amount >= 500:
            embed = EmbedBuilder(
                title="Congratulations!",
                description="You meet the basic requirements for staff. You may apply for staff below.",
                fields=fields,
                color=0x39FF14,  # GREEN
            ).build()
            await ctx.respond(embed=embed, ephemeral=True, view=StaffAppView())
        else:
            wait_time = max(
                timedelta(weeks=52) - time_since_creation,
                timedelta(days=30) - time_since_join,
            )

            embed = EmbedBuilder(
                title="Missing Requirements",
                description=f"""Unfortunately, you do not meet the basic requirements in order to apply for staff.
                Your account must be at least 1 year old, you must have been a member of the server for at least 
                30 days and you need to have at least 500 messages sent totalin any channel.""" + 
                f"""You will be eligible to apply for staff in **{precisedelta(wait_time, minimum_unit='days', format="%.0F")}**.""" if msg_amount > 500 else "" +
                f"""You need to send **{(left := 500 - msg_amount)}** more message{"" if left == 1 else "s"}.""" if msg_amount < 500 else "",
                fields=fields,
                color=0xFF0000,  # RED
            ).build()
            await ctx.respond(embed=embed, ephemeral=True)

        log(f"User {account} checked their requirements in {ctx.guild}.")


def setup(bot: commands.Bot) -> None:
    bot.add_cog(StaffRequirement(bot))
