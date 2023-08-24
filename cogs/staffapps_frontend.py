from __future__ import annotations

from datetime import datetime, timedelta
from os import getenv
from time import time

import discord
import discord.ui
from discord.ext import commands
from humanize import precisedelta

import database
from message_formatting.embeds import EmbedBuilder
from util.limiter import limit
from util.logger import log


class embeds:
    """
    This class creates embeds when a user is DENIED for an application.
    See docstrings below for reasons a user can be DENIED.
    """

    def __init__(self) -> None:
        pass

    def min_reqs(
        self,
        msg_count: int,
        join_time: datetime,
        created_at: datetime,
    ) -> discord.Embed:
        """
        User does not meet the minimum requirements to apply for staff.
        """
        time_since_creation = datetime.now(tz=created_at.tzinfo) - created_at
        time_since_join = datetime.now(tz=join_time.tzinfo) - join_time

        fields = [
            [
                "Created",
                f"""{created_at.strftime('%B %d, %Y')}
                {precisedelta(time_since_creation, minimum_unit='days', format="%.0F")} ago""",
                True,
            ],
            [
                "Joined",
                f"""{join_time.strftime('%B %d, %Y')}
                {precisedelta(time_since_join, minimum_unit='days', format="%.0F")} ago""",
                True,
            ],
            ["Messages", f"{msg_count} messages", True],
        ]

        wait_time = max(
            timedelta(weeks=52) - time_since_creation,
            timedelta(days=30) - time_since_join,
        )
        desc = """Unfortunately, you do not meet the basic requirements in order to apply for staff.
            Your account must be at least 1 year old, you must have been a member of the server for at least 30 days and you need to have at least 500 messages sent total in any channel. (sent after November 20th 2022)"""
        if wait_time > timedelta(0):
            desc += f"""\n\nYou will be eligible to apply for staff in **{precisedelta(wait_time, minimum_unit='days', format="%.0F")}**."""
        if msg_count < 500:
            desc += f"""\n\nYou need to send **{(left := 500 - msg_count)}** more message{"" if left == 1 else "s"}."""
        return EmbedBuilder(
            title="Missing Requirements",
            description=desc,
            fields=fields,
            color=0xFF0000,  # RED
        ).build()

    def marked_spam(self) -> discord.Embed:
        """
        User is marked spam by staff for a previous offence.
        """
        return EmbedBuilder(
            title="You cannot apply for staff!",
            description="Unfortunately, you cannot apply for staff at this time. If you believe this is a mistake, please contact a staff member.",
            color=0xFF0000,  # RED
        ).build()

    def cooldown(self, cooldown: int) -> discord.Embed:
        """
        User has recently applied for staff and was denied.
        A cooldown is in place to prevent a user from immediatly re-applying.
        """
        curtime = datetime.now()
        cooldown_time = datetime.fromtimestamp(cooldown)
        time_left = cooldown_time - curtime
        return EmbedBuilder(
            title="You have recently applied for staff!",
            description=f"You cannot apply for staff for another **{precisedelta(time_left, minimum_unit='days', format='%.0F')}** because your previous application has recently been reviewed.",
            color=0xFF0000,  # RED
        ).build()

    def ongoing(self) -> discord.Embed:
        """
        User still has an ongoing application.
        """
        return EmbedBuilder(
            title="You have already applied for staff!",
            description="Your application has already been submitted. We will review it and get back to you as soon as possible.",
            color=0xFFD700,  # GOLD
        ).build()


class user:
    def __init__(self, user: discord.Member) -> None:
        """
        This class represents a read-only user who is applying for staff.
        Data is accurate at the time of object creation.
        """
        # connect to database
        db = database.connect()
        cursor = db.cursor()
        # get user data from discord
        self.uid = user.id
        self.joined_at = user.joined_at
        self.created_at = user.created_at
        # get user data from database
        # check if user exists, else add
        messages_sent = (
            None
            if (
                sent := cursor.execute(
                    "SELECT messagesSent, helpMessagesSent FROM user WHERE uid = ?",
                    (user.id,),
                ).fetchall()
            )
            == []
            else sent
        )
        # If a user is not in db, add them
        if messages_sent is None:
            self.add_user(user.id)

        self.messages_sent = cursor.execute(
            "SELECT messagesSent FROM user WHERE uid = ?",
            (self.uid,),
        ).fetchone()[0]
        self.marked_spam = cursor.execute(
            "SELECT markedSpam FROM user WHERE uid = ?",
            (self.uid,),
        ).fetchone()[0]
        self.cooldown = float(
            cursor.execute(
                "SELECT cooldown FROM user WHERE uid = ?",
                (self.uid,),
            ).fetchone()[0]
            or 0,
        )
        # get all statuses
        self.status = [
            x[0]
            for x in cursor.execute(
                "SELECT status FROM application WHERE uid = ?",
                (self.uid,),
            ).fetchall()
        ]
        # close database connection
        db.close()

    def __str__(self) -> str:
        """
        String representation of the user.
        """
        return f"User: {self.uid}, Joined: {self.joined_at}, Messages: {self.messages_sent}, Marked Spam: {self.marked_spam}, Cooldown: {self.cooldown}"

    def __repr__(self) -> str:
        """
        Same as __str__.
        """
        return f"User: {self.uid}, Joined: {self.joined_at}, Messages: {self.messages_sent}, Marked Spam: {self.marked_spam}, Cooldown: {self.cooldown}"

    def add_user(self, uid: int) -> None:
        self.cursor.execute(
            "INSERT INTO user VALUES (?, ?, ?, ?, ?)",
            (uid, 0, False, None, 0),
        )  # See ERD.mdj

    def min_reqs(self) -> tuple[bool, int, datetime]:
        """
        Returns a tuple of (bool, int, datetime) where bool is True if the user meets the minimum requirements to apply for staff.
        """
        time_since_join = datetime.now(tz=self.joined_at.tzinfo) - self.joined_at
        if (
            self.joined_at
            <= (datetime.now(tz=self.joined_at.tzinfo) - timedelta(days=30))
            and self.messages_sent >= 500
        ):
            return (True, self.messages_sent, time_since_join)
        return (False, self.messages_sent, time_since_join)

    def is_on_cooldown(self) -> bool:
        """
        Returns True if the user is on cooldown.
        """
        return (self.cooldown - time() // 1) > 0


class StaffAppView(discord.ui.View):
    def __init__(self, author: user, bot: commands.Bot) -> None:
        """
        A discord view for the staff application.
        Includes a select menu for:
            - NDA
            - Timezone
            - Hours Available
        """
        super().__init__()
        self.author = author
        self.bot = bot

    @discord.ui.select(
        placeholder="Do you agree to the Non-Disclosure Agreement?",
        row=0,
        min_values=1,
        max_values=1,
        options=[
            discord.SelectOption(
                label="I Agree",
                description="I agree to the Non-Disclosure Agreement.",
                emoji="✅",
            ),
            discord.SelectOption(
                label="I do NOT Agree",
                description="I do not agree to the Non-Disclosure Agreement.",
                emoji="❌",
            ),
        ],
    )
    async def nda_callback(
        self,
        select: discord.ui.Select,
        interaction: discord.Interaction,
    ) -> None:
        """
        If the user does not agree to the NDA, the application is cancelled.
        """
        answer = select.values[0]
        if answer == "I do NOT Agree":
            embed = discord.Embed(
                title="Staff Application",
                description="You have not agreed to the Non-Disclosure Agreement.\n Unfortunately, we cannot complete your staff application without your agreement. Please re-apply when you are ready to agree to the Non-Disclosure Agreement.\n *(You can re-apply by running this command again)*",
                color=0xFF0000,
            )
            await interaction.response.edit_message(embed=embed, view=None)
            return
        self.nda = True
        self.children[1].disabled = False
        select.disabled = True
        await interaction.response.edit_message(view=self)

    @discord.ui.select(
        placeholder="What is your timezone?",
        row=1,
        min_values=1,
        max_values=1,
        disabled=True,
        options=[
            discord.SelectOption(
                label="UTC-12:00",
                description="International Date Line West",
            ),
            discord.SelectOption(label="UTC-11:00", description="Midway Island, Samoa"),
            discord.SelectOption(label="UTC-10:00", description="Hawaii"),
            discord.SelectOption(label="UTC-09:00", description="Alaska"),
            discord.SelectOption(
                label="UTC-08:00",
                description="Pacific Time (US & Canada)",
            ),
            discord.SelectOption(
                label="UTC-07:00",
                description="Mountain Time (US & Canada)",
            ),
            discord.SelectOption(
                label="UTC-06:00",
                description="Central Time (US & Canada)",
            ),
            discord.SelectOption(
                label="UTC-05:00",
                description="Eastern Time (US & Canada)",
            ),
            discord.SelectOption(
                label="UTC-04:00",
                description="Atlantic Time (Canada)",
            ),
            discord.SelectOption(label="UTC-03:00", description="Brasilia"),
            discord.SelectOption(label="UTC-02:00", description="Mid-Atlantic"),
            discord.SelectOption(label="UTC-01:00", description="Cape Verde Is."),
            discord.SelectOption(label="UTC+00:00", description="Casablanca, Monrovia"),
            discord.SelectOption(
                label="UTC+01:00",
                description="Amsterdam, Berlin, Rome",
            ),
            discord.SelectOption(
                label="UTC+02:00",
                description="Cairo, Helsinki, Kaliningrad",
            ),
            discord.SelectOption(
                label="UTC+03:00",
                description="Moscow, Nairobi, Baghdad",
            ),
            discord.SelectOption(label="UTC+04:00", description="Abu Dhabi, Muscat"),
            discord.SelectOption(
                label="UTC+05:00",
                description="Islamabad, Karachi, Tashkent",
            ),
            discord.SelectOption(label="UTC+06:00", description="Almaty, Dhaka"),
            discord.SelectOption(
                label="UTC+07:00",
                description="Bangkok, Hanoi, Jakarta",
            ),
            discord.SelectOption(
                label="UTC+08:00",
                description="Beijing, Perth, Singapore",
            ),
            discord.SelectOption(label="UTC+09:00", description="Tokyo, Seoul, Osaka"),
            discord.SelectOption(
                label="UTC+10:00",
                description="Brisbane, Canberra, Melbourne",
            ),
            discord.SelectOption(
                label="UTC+11:00",
                description="Magadan, Solomon Is., New Caledonia",
            ),
            discord.SelectOption(label="UTC+12:00", description="Auckland, Wellington"),
            # Thank god for Copilot xoxo
        ],
    )
    async def timezone_callback(
        self,
        select: discord.ui.Select,
        interaction: discord.Interaction,
    ) -> None:
        self.timezone = select.values[0]
        select.disabled = True
        self.children[2].disabled = False
        await interaction.response.edit_message(view=self)

    @discord.ui.select(
        placeholder="How many hours a week can you commit to the server?",
        row=2,
        min_values=1,
        max_values=1,
        disabled=True,
        options=[
            discord.SelectOption(
                label="1 - 2 Hours",
            ),
            discord.SelectOption(
                label="3 - 4 Hours",
            ),
            discord.SelectOption(
                label="5 - 6 Hours",
            ),
            discord.SelectOption(
                label="7 - 8 Hours",
            ),
            discord.SelectOption(
                label="8 - 12 Hours",
            ),
            discord.SelectOption(
                label="12 - 15 Hours",
            ),
            discord.SelectOption(
                label="15 - 20 Hours",
            ),
            discord.SelectOption(
                label="20+ Hours",
            ),
        ],
    )
    async def time_callback(
        self,
        select: discord.ui.Select,
        interaction: discord.Interaction,
    ) -> None:
        self.time_per_wk = select.values[0]
        self.children[3].disabled = False
        select.disabled = True
        await interaction.response.edit_message(view=self)

    @discord.ui.button(
        label="Next Questions",
        style=discord.ButtonStyle.primary,
        row=3,
        disabled=True,
    )
    async def button_callback(
        self,
        button: discord.ui.Button,
        interaction: discord.Interaction,
    ) -> None:
        """
        Sends a modal with the next questions
        """
        await interaction.response.send_modal(
            StaffAppModal(
                self.author,
                self.nda,
                self.timezone,
                self.time_per_wk,
                self.bot,
                title="Input answers",
            ),
        )


class StaffAppModal(discord.ui.Modal):
    def __init__(
        self,
        author: discord.Member,
        nda: bool,
        timezone: str,
        hours_per_wk: str,
        bot: commands.Bot,
        *args,
        **kwargs,
    ) -> None:
        """
        A discord modal that asks the user for their answers to the questions.
        After all answers are given, insert the answers (also from staffAppView) into the database.
        """
        super().__init__(*args, **kwargs)
        self.db = database.connect()
        self.cursor = self.db.cursor()
        self.bot = bot

        self.author = author
        self.nda = nda
        self.timezone = timezone
        self.hours_per_wk = hours_per_wk

        self.add_item(
            discord.ui.InputText(
                label="First Name (Eg. John)",
                style=discord.InputTextStyle.short,
            ),
        )
        self.add_item(
            discord.ui.InputText(
                label="Why do you want to become a staff member",
                style=discord.InputTextStyle.long,
            ),
        )
        self.add_item(
            discord.ui.InputText(
                label="How can you contribute if you are given staff",
                style=discord.InputTextStyle.long,
            ),
        )

    async def callback(self, interaction: discord.Interaction) -> None:
        # New discord names
        if str(self.author.discriminator) == "0":
            self.discord_name = f"@{self.author.name}"
        else:
            self.discord_name = f"{self.author.name}#{self.author.discriminator}"

        self.cursor.execute(
            """
        INSERT INTO application (
            uid,
            status,
            discordName,
            firstName,
            nda,
            timezone,
            hoursAvailableWk,
            staffReason,
            contributeReason,
            submissionTime
        )
        VALUES (
            ?, ?, ?, ?, ?, ?, ?, ?, ?, ?
        )
        """,
            (
                self.author.id,
                1,
                self.discord_name,
                self.children[0].value,
                self.nda,
                self.timezone,
                self.hours_per_wk,
                self.children[1].value,
                self.children[2].value,
                str(int(time() // 1)),
            ),
        )
        self.db.commit()
        self.db.close()
        # Send message to staff channel
        staff_channel = self.bot.get_channel(int(getenv("STAFF_CHANNEL")))
        text = f"{self.author.mention} has submitted a new staff application!"
        await staff_channel.send(text)
        # Send message to user
        embed = discord.Embed(
            title="Staff Application successfully submitted",
            description="Thank you for your application! If your application gets accepted, you will be contacted by a staff member.",
            color=0xFFD700,
        )
        await interaction.response.edit_message(embed=embed, content="", view=None)
        log("$ has completed the Staff Application", self.author)


class StaffAppsUser(commands.Cog):
    """
    Main cog for the staff application system (end-user commands)
    """

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @commands.slash_command(
        name="apply-for-staff",
        description="Apply for a staff position if your account meets the requirements!",
    )
    @limit(1)
    async def apply(self, ctx: commands.Context) -> None:
        """
        Lets users apply for staff positions
        """

        # DM check
        if ctx.guild_id is None:
            embed = EmbedBuilder(
                "You cannot use this command in DMs",
                "Please use this command in the HWH server",
                0xFF0000,
            ).build()
            await ctx.respond(embed=embed, ephemeral=True)
            return

        # create user class, with care for new discord names
        if str(ctx.author.discriminator) == "0":
            logname = f"@{ctx.author.name}:{ctx.author.id}"
        else:
            logname = f"{ctx.author.name}#{ctx.author.discriminator}:{ctx.author.id}"
        applicant = user(ctx.author)

        # check if user is banned
        if applicant.marked_spam:
            await ctx.respond(embed=embeds().marked_spam(), ephemeral=True)
            log(f"{logname} tried to apply for staff but is marked as spam")
            return

        # check cooldown
        if applicant.is_on_cooldown():
            await ctx.respond(
                embed=embeds().cooldown(applicant.cooldown),
                ephemeral=True,
            )
            log(f"{logname} tried to apply for staff but is on cooldown")
            return

        # check app status
        status = any(
            x in [1, 3, 4, 5, 6, 7, 8] for x in applicant.status
        )  # 2 and 8 are closed applications, others are open
        if status:
            await ctx.respond(embed=embeds().ongoing(), ephemeral=True)
            log(
                f"{logname} tried to apply for staff but already has an ongoing application",
            )
            return

        # check minimum requirements
        if not applicant.min_reqs()[0]:
            await ctx.respond(
                embed=embeds().min_reqs(
                    applicant.min_reqs()[1],
                    applicant.joined_at,
                    applicant.created_at,
                ),
                ephemeral=True,
            )
            log(
                f"{logname} tried to apply for staff but does not meet the minimum requirements",
            )
            return

        log(f"{logname} is applying for staff")
        # user meets all requirements, send application form
        embed = EmbedBuilder(
            title="Congratulations!",
            description="""You meet the basic requirements for staff. You may apply for staff below.\nPlease make sure you read the following requirements,
        If you do not fulfill the requirements, please contact us via ModMail if you feel you have a special circumstance before submitting the application.
        If not, do not continue, and please apply once you have fulfilled them.
        You will not receive a response if you have not received a waiver or if you obviously do not meet the requirements\n\n
                    I am at least 18 years old.
                    I am mature and unbiased.
                    I am willing to partake in an interview.
                    I did not receive any infractions in the past three (3) months.


        **Non-disclosure agreement**
        You agree not to disclose any information within the staff channels and/or any confidential Homework Help assets without explicit leave.\n""",
            fields=None,
            color=0x39FF14,  # GREEN
        ).build()
        await ctx.respond(
            embed=embed,
            ephemeral=True,
            view=StaffAppView(ctx.author, self.bot),
        )


def setup(bot: commands.Bot) -> None:
    bot.add_cog(StaffAppsUser(bot))
