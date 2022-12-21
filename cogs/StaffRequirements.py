from datetime import datetime, timedelta
from os import getenv

import discord.ui
from discord.ext import commands
from humanize import precisedelta

import sqlite3
from time import time

from util.EmbedBuilder import EmbedBuilder
from util.Logging import log

#TODO: Clean up text in the congrats embed
#TODO: Add logging
#TODO: Clean code

class StaffAppView(discord.ui.View):
    def __init__(self, db, author):
        super().__init__()
        self.db = db
        self.cursor = self.db.cursor()
        self.author = author


    @discord.ui.select( 
        placeholder = "Do you agree to the Non-Disclosure Agreement?",
        row=0,
        min_values = 1,
        max_values = 1,
        options = [
            discord.SelectOption(
                label="I Agree",
                description="I agree to the Non-Disclosure Agreement.",
                emoji="✅"
            ),
            discord.SelectOption(
                label="I do NOT Agree",
                description="I do not agree to the Non-Disclosure Agreement.",
                emoji="❌"
            )
        ]
    )
    async def nda_callback(self, select, interaction):
        self.cursor.execute("UPDATE staffapp SET nda = ? WHERE uid = ?", (True if (answer := select.values[0]) == "I Agree" else False, interaction.user.id))
        self.db.commit()
        if answer == "I do NOT Agree":
            embed = discord.Embed(
                title="Staff Application",
                description="You have not agreed to the Non-Disclosure Agreement.\n Unfortunately, we cannot complete your staff application without your agreement. Please re-apply when you are ready to agree to the Non-Disclosure Agreement.\n *(You can re-apply by running this command again)*",
                color=0xFF0000
            )
            await interaction.response.edit_message(embed=embed, view=None)
            return
        else:
            self.children[1].disabled = False
            select.disabled = True
            await interaction.response.edit_message(view=self)

    
    @discord.ui.select(
        placeholder = "What is your timezone?",
        row=1,
        min_values = 1,
        max_values = 1,
        disabled=True,
        options = [
            discord.SelectOption(
                label="UTC-12:00",
                description="International Date Line West"
            ),
            discord.SelectOption(
                label="UTC-11:00",
                description="Midway Island, Samoa"
            ),
            discord.SelectOption(
                label="UTC-10:00",
                description="Hawaii"
            ),
            discord.SelectOption(
                label="UTC-09:00",
                description="Alaska"
            ),
            discord.SelectOption(
                label="UTC-08:00",
                description="Pacific Time (US & Canada)"
            ),
            discord.SelectOption(
                label="UTC-07:00",
                description="Mountain Time (US & Canada)"
            ),
            discord.SelectOption(
                label="UTC-06:00",
                description="Central Time (US & Canada)"
            ),
            discord.SelectOption(
                label="UTC-05:00",
                description="Eastern Time (US & Canada)"
            ),
            discord.SelectOption(
                label="UTC-04:00",
                description="Atlantic Time (Canada)"
            ),
            discord.SelectOption(
                label="UTC-03:00",
                description="Brasilia"
            ),
            discord.SelectOption(
                label="UTC-02:00",
                description="Mid-Atlantic"
            ),
            discord.SelectOption(
                label="UTC-01:00",
                description="Cape Verde Is."
            ),
            discord.SelectOption(
                label="UTC+00:00",
                description="Casablanca, Monrovia"
            ),
            discord.SelectOption(
                label="UTC+01:00",
                description="Amsterdam, Berlin, Rome"
            ),
            discord.SelectOption(
                label="UTC+02:00",
                description="Cairo, Helsinki, Kaliningrad"
            ),
            discord.SelectOption(
                label="UTC+03:00",
                description="Moscow, Nairobi, Baghdad"
            ),
            discord.SelectOption(
                label="UTC+04:00",
                description="Abu Dhabi, Muscat"
            ),
            discord.SelectOption(
                label="UTC+05:00",
                description="Islamabad, Karachi, Tashkent"
            ),
            discord.SelectOption(
                label="UTC+06:00",
                description="Almaty, Dhaka"
            ),
            discord.SelectOption(
                label="UTC+07:00",
                description="Bangkok, Hanoi, Jakarta"
            ),
            discord.SelectOption(
                label="UTC+08:00",
                description="Beijing, Perth, Singapore"
            ),
            discord.SelectOption(
                label="UTC+09:00",
                description="Tokyo, Seoul, Osaka"
            ),
            discord.SelectOption(
                label="UTC+10:00",
                description="Brisbane, Canberra, Melbourne"
            ),
            discord.SelectOption(
                label="UTC+11:00",
                description="Magadan, Solomon Is., New Caledonia"
            ),
            discord.SelectOption(
                label="UTC+12:00",
                description="Auckland, Wellington"
            ),
            # Thank god for Copilot xoxo
        ]
    )
    async def timezone_callback(self, select, interaction):
        self.cursor.execute("UPDATE staffapp SET timezone = ? WHERE uid = ?", (select.values[0], interaction.user.id))
        self.db.commit()
        select.disabled = True
        self.children[2].disabled = False
        await interaction.response.edit_message(view=self)
    
    @discord.ui.select( 
        placeholder = "How many hours a week can you commit to the server?",
        row=2,
        min_values = 1,
        max_values = 1,
        disabled=True,
        options = [
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

        ]
    )
    async def time_callback(self, select, interaction):
        self.cursor.execute("UPDATE staffapp SET hours_available_wk = ? WHERE uid = ?", (select.values[0], interaction.user.id))
        self.db.commit()
        self.children[3].disabled = False
        select.disabled = True
        await interaction.response.edit_message(view=self)
    
    @discord.ui.button(label="Next Questions", style=discord.ButtonStyle.primary, row=3, disabled=True)
    async def button_callback(self, button, interaction):
        await interaction.response.send_modal(StaffAppModal(self.db, self.author, title="Input answers"))


class StaffAppModal(discord.ui.Modal):
    def __init__(self, db, author, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.db = db
        self.cursor = self.db.cursor()
        self.author = author

        self.add_item(discord.ui.InputText(label="First Name (Eg. John)", style=discord.InputTextStyle.short))
        self.add_item(discord.ui.InputText(label="Why do you want to become a staff member", style=discord.InputTextStyle.long))
        self.add_item(discord.ui.InputText(label="How can you contribute if you are given staff", style=discord.InputTextStyle.long))
    
    async def disable_if_done(self, interaction):
        if all([True if field_content != None else False for field_content in self.cursor.execute('SELECT * FROM staffapp WHERE uid = ?', (self.author,)).fetchone()]): #? this if statement is an artifact from when answers didn't need to be answered in order
            #TODO change color, change text
            embed = discord.Embed(
                title="Staff Application",
                description="Thank you for your application! We will review it and get back to you as soon as possible.",
                color=0xFFD700
            )
            await interaction.response.edit_message(embed=embed, content="", view=None)
            return True
        return False

    async def callback(self, interaction: discord.Interaction):
        self.cursor.execute("UPDATE staffapp SET first_name = ?, staff_reason = ?, contribute_reason = ?, submission_time = ? WHERE uid = ?", (self.children[0].value, self.children[1].value, self.children[2].value, time() // 1 ,interaction.user.id))
        self.db.commit()
        await self.disable_if_done(interaction)

class StaffRequirement(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.db= sqlite3.connect("util/database.sqlite")
        self.cursor = self.db.cursor()
        self.cursor.execute("""CREATE TABLE IF NOT EXISTS staffapp (
            uid INTEGER PRIMARY KEY,
            discord_name TEXT,
            first_name TEXT,
            nda BOOLEAN,
            timezone TEXT,
            hours_available_wk TEXT,
            staff_reason TEXT,
            contribute_reason TEXT,
            submission_time INTEGER
        )""")

    def fetch_message_count(self, uid):
        try:
            self.cursor.execute("SELECT amount FROM messagecount WHERE uid = ?", (uid,))
            return self.cursor.fetchone()[0]
        except TypeError:
            return 0

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
        self.author = ctx.author.id
        # check if the user has answered every field in the staffapp table
        try:
            filled_in = all([True if field_content != None else False for field_content in self.cursor.execute('SELECT * FROM staffapp WHERE uid = ?', (ctx.author.id,)).fetchone()])
        except TypeError:
            filled_in = False
        if filled_in:
            embed = discord.Embed(
                title="You have already applied for staff!",
                description="Your application has already been submitted. We will review it and get back to you as soon as possible.",
                color=0xFFD700,
            )
            await ctx.respond(embed=embed, ephemeral=True)
            return

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
        # time since join is at least 30 days AND
        # message amount is at least 500
        if time_since_creation >= timedelta(weeks=52) and time_since_join >= timedelta(
            days=30
        ) and msg_amount >= 500:
            # user is eligible to apply for staff, add to db
            self.cursor.execute("INSERT INTO staffapp (uid, discord_name) VALUES (?, ?) ON CONFLICT (uid) DO NOTHING", (ctx.author.id, f"{ctx.author.name}#{ctx.author.discriminator}"))
            self.db.commit()
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
                fields=fields,
                color=0x39FF14,  # GREEN
            ).build()
            await ctx.respond(embed=embed, ephemeral=True, view=StaffAppView(self.db, self.author))
        else:
            wait_time = max(
                timedelta(weeks=52) - time_since_creation,
                timedelta(days=30) - time_since_join,
            )
            desc = f"""Unfortunately, you do not meet the basic requirements in order to apply for staff.
                Your account must be at least 1 year old, you must have been a member of the server for at least 30 days and you need to have at least 500 messages sent total in any channel. (sent after November 20th 2022)"""
            if wait_time > timedelta(0):
                desc += f"""\n\nYou will be eligible to apply for staff in **{precisedelta(wait_time, minimum_unit='days', format="%.0F")}**."""
            if msg_amount < 500:
                desc += f"""\n\nYou need to send **{(left := 500 - msg_amount)}** more message{"" if left == 1 else "s"}."""
            embed = EmbedBuilder(
                title="Missing Requirements",
                description=desc,
                fields=fields,
                color=0xFF0000,  # RED
            ).build()
            await ctx.respond(embed=embed, ephemeral=True)

        log(f"User {account} checked their requirements in {ctx.guild}.")


def setup(bot: commands.Bot) -> None:
    bot.add_cog(StaffRequirement(bot))
