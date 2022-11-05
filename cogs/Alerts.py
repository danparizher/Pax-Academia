import re
import sqlite3

import discord
from discord.ext import commands

from util.EmbedBuilder import EmbedBuilder
from util.Logging import log


class Alerts(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.db = sqlite3.connect("util/alerts.db")
        c = self.db.cursor()
        c.execute("CREATE TABLE IF NOT EXISTS alerts (keyword TEXT, user_id INTEGER)")
        self.db.commit()

    # Allows the user to enter a keyword to be alerted when it is mentioned in the guild. When the keyword is used, the bot will send a DM to the user.
    @commands.slash_command(
        name="add-alert", description="Adds an alert for a keyword."
    )
    async def add_alert(self, ctx: commands.Context, keyword: str) -> None:
        # Check if the keyword is already in the database.
        c = self.db.cursor()
        c.execute("SELECT * FROM alerts WHERE keyword = ?", (keyword,))
        if c.fetchone():
            embed = EmbedBuilder(
                title="Error",
                description="This keyword is already in the database.",
            ).build()
            await ctx.respond(embed=embed, ephemeral=True)
            return

        # Add the keyword to the database.
        c.execute("INSERT INTO alerts VALUES (?, ?)", (keyword, ctx.author.id))
        self.db.commit()

        embed = EmbedBuilder(
            title="Success",
            description=f"Added alert for keyword `{keyword}`.",
        ).build()
        await ctx.respond(embed=embed, ephemeral=True)

        log(f"Alert added by {ctx.author} in {ctx.guild}.")

    # Allows the user to remove an alert for a keyword.
    @commands.slash_command(
        name="remove-alert",
        description="Removes an alert for a keyword.",
    )
    async def remove_alert(self, ctx: commands.Context, keyword: str) -> None:
        # Check if the keyword is in the database.
        c = self.db.cursor()
        c.execute("SELECT * FROM alerts WHERE keyword = ?", (keyword,))
        if not c.fetchone():
            embed = EmbedBuilder(
                title="Error",
                description="This keyword is not in the database.",
            ).build()
            await ctx.respond(embed=embed, ephemeral=True)
            return

        # Remove the keyword from the database.
        c.execute("DELETE FROM alerts WHERE keyword = ?", (keyword,))
        self.db.commit()

        embed = EmbedBuilder(
            title="Success",
            description=f"Removed alert for keyword `{keyword}`.",
        ).build()
        await ctx.respond(embed=embed, ephemeral=True)

        log(f"Alert removed by {ctx.author} in {ctx.guild}.")

    @commands.slash_command(name="list-alerts", description="Lists all alerts.")
    async def list_alerts(self, ctx: commands.Context) -> None:
        # Get all alerts from the database.
        c = self.db.cursor()
        c.execute("SELECT * FROM alerts")
        alerts = c.fetchall()

        # Create a list of all alerts.
        alert_list = ""
        for alert in alerts:
            alert_list += f"`{alert[0]}`\n"

        # respond the list of alerts.
        embed = EmbedBuilder(
            title="Alerts",
            description=alert_list,
        ).build()
        await ctx.respond(embed=embed, ephemeral=True)

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message) -> None:
        # Ignore messages from bots.
        if message.author.bot:
            return

        # Ignore messages that do not contain a keyword.
        c = self.db.cursor()
        c.execute("SELECT * FROM alerts")
        keywords = c.fetchall()
        if not any(keyword[0] in message.content for keyword in keywords):
            return

        # Send a DM to the user who added the alert.
        for keyword in keywords:
            if keyword[0] in message.content:
                user = self.bot.get_user(keyword[1]) or message.author
                embed = EmbedBuilder(
                    title="Alert",
                    description=f"Keyword `{keyword[0]}` was mentioned in {message.channel.mention} by {message.author.mention}.",
                ).build()
                await user.send(embed=embed)


def setup(bot) -> None:
    bot.add_cog(Alerts(bot))
