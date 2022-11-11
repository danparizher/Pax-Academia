import re
import sqlite3

import discord
from discord.commands import option
from discord.ext import commands

from util.EmbedBuilder import EmbedBuilder
from util.Logging import log


def get_keywords(ctx: discord.AutocompleteContext) -> list:
    conn = sqlite3.connect("util/alerts.db")
    data = [
        keyword[0]
        for keyword in conn.cursor()
        .execute(
            "SELECT keyword FROM alerts WHERE user_id = ? AND author_name = ?",
            (ctx.interaction.user.id, ctx.interaction.user.name),
        )
        .fetchall()
    ]
    conn.close()
    return data


class Alerts(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.db = sqlite3.connect("util/alerts.db")
        c = self.db.cursor()
        c.execute(
            "CREATE TABLE IF NOT EXISTS alerts (keyword TEXT, user_id INTEGER, author_name TEXT)"
        )
        self.db.commit()

    # Allows the user to enter a keyword to be alerted when it is mentioned in the guild. When the keyword is used, the bot will send a DM to the user.
    @commands.slash_command(
        name="add-alert", description="Adds an alert for a keyword."
    )
    async def add_alert(self, ctx: commands.Context, keyword: str) -> None:
        # Check if the keyword is already in the database.
        c = self.db.cursor()
        c.execute(
            "SELECT * FROM alerts WHERE keyword = ? AND user_id = ?",
            (keyword, ctx.author.id),
        )
        if c.fetchone():
            embed = EmbedBuilder(
                title="Error",
                description="This keyword is already in the database.",
            ).build()
            await ctx.respond(embed=embed, ephemeral=True)
            return

        # Add the keyword to the database.
        c.execute(
            "INSERT INTO alerts VALUES (?, ?, ?)",
            (keyword, ctx.author.id, ctx.author.name),
        )
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
    @option(
        name="keyword",
        description="The keyword to remove.",
        autocomplete=get_keywords,
    )
    async def remove_alert(
        self,
        ctx: commands.Context,
        keyword: str,
    ) -> None:

        # Check if the keyword is in the database.
        c = self.db.cursor()
        c.execute(
            "SELECT * FROM alerts WHERE keyword = ? AND user_id = ?",
            (keyword, ctx.author.id),
        )
        if not c.fetchone():
            embed = EmbedBuilder(
                title="Error",
                description="This keyword is not in the database.",
            ).build()
            await ctx.respond(embed=embed, ephemeral=True)
            return

        # Remove the keyword from the database.
        c.execute(
            "DELETE FROM alerts WHERE keyword = ? AND user_id = ?",
            (keyword, ctx.author.id),
        )
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
        c.execute("SELECT * FROM alerts WHERE user_id = ?", (ctx.author.id,))
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
        async def user_alerts() -> None:
            if (
                message.author.bot
                or message.channel not in message.author.guild.channels
                or not message.author.guild.get_member(self.bot.user.id)
            ):
                return

            # Ignore messages that do not contain a keyword.
            c = self.db.cursor()
            c.execute("SELECT * FROM alerts")
            keywords = c.fetchall()
            if not any(
                re.search(keyword[0], message.content, re.IGNORECASE)
                for keyword in keywords
            ):
                return

            # Send a DM to the user who added the alert.
            for keyword in keywords:
                if re.search(keyword[0], message.content, re.IGNORECASE):
                    user = await self.bot.fetch_user(keyword[1])
                    embed = EmbedBuilder(
                        title="Alert",
                        description=f"Your keyword `{keyword[0]}` was mentioned in {message.channel.mention} by {message.author.mention}.",
                        fields=[
                            ("Message", message.content, False),
                            (
                                "Message Link",
                                f"[Click to see message]({message.jump_url})",
                                False,
                            ),
                        ],
                    ).build()
                    try:
                        await user.send(embed=embed)
                    except discord.Forbidden:
                        pass

        async def tutor_alerts(self, message: discord.Message) -> None:
            if (
                message.author.id == self.bot.user.id
                or message.guild.id != 238956364729155585
                or message.author.bot
            ):
                return

            keywords = [
                "dm me",
                "pay",
                "paypal",
                "cash",
                "venmo",
                "dollar",
                "tutor",
                "money",
                "price",
                "$",
                "professional",
                "service",
                "fee",
            ]
            tutor_logs = self.bot.get_channel(1038985540147626024)
            # fmt: off
            if any(temp := sorted((lambda y: [x.group(0) for x in y if x != ""])([re.search(keyword, message.content, re.IGNORECASE) or "" for keyword in keywords]), key=lambda x: len(x), reverse=True,)):
            # fmt: on
                embed = EmbedBuilder(
                    title="Alert",
                    description=f"{message.author.mention} mentioned `{temp[0]}` in {message.channel.mention}.",
                    fields=[
                        ("Message", message.content, False),
                        (
                            "Message Link",
                            f"[Click to see message]({message.jump_url})",
                            False,
                        ),
                    ],
                ).build()
                await tutor_logs.send(embed=embed)

        await user_alerts()
        await tutor_alerts(self, message)

    @commands.slash_command(name="view-db", description="View the database.")
    async def view_db(self, ctx: commands.Context) -> None:
        await ctx.respond(
            content="Alerts Database",
            file=discord.File("util/alerts.db"),
            ephemeral=True,
        )


def setup(bot) -> None:
    bot.add_cog(Alerts(bot))
