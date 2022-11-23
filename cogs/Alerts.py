import re
import sqlite3
import base64

import discord
from discord.commands import option
from discord.ext import commands

from util.EmbedBuilder import EmbedBuilder
from util.Logging import log


# used to encode/ decode user input to protect against SQLi
b64ify = lambda x: base64.b64encode(x.encode()).decode()
deb64ify = lambda y: base64.b64decode(y.encode()).decode()


def get_keywords(ctx: discord.AutocompleteContext) -> list:
    """
    It gets all the keywords from the database for the user who is currently using the command

    :param ctx: discord.AutocompleteContext
    :type ctx: discord.AutocompleteContext
    :return: A list of keywords that the user has set up for alerts.
    """
    conn = sqlite3.connect("util/database.sqlite")
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
    return [deb64ify(item) for item in data]


class Alerts(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.db = sqlite3.connect("util/database.sqlite")
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
        """
        It checks if the keyword is already in the database, if it is, it sends an error message, if it
        isn't, it adds the keyword to the database and sends a success message.

        :param ctx: commands.Context
        :type ctx: commands.Context
        :param keyword: str
        :type keyword: str
        :return: The return type is None.
        """
        b64_keyword = b64ify(keyword)

        c = self.db.cursor()
        c.execute(
            "SELECT * FROM alerts WHERE keyword = ? AND user_id = ?",
            (b64_keyword, ctx.author.id),
        )
        if c.fetchone():
            embed = EmbedBuilder(
                title="Error",
                description="This keyword is already in the database.",
            ).build()
            await ctx.respond(embed=embed, ephemeral=True)
            return

        c.execute(
            "INSERT INTO alerts VALUES (?, ?, ?)",
            (b64_keyword, ctx.author.id, ctx.author.name),
        )
        self.db.commit()

        embed = EmbedBuilder(
            title="Success",
            description=f"Added alert for keyword `{keyword}`.",
        ).build()
        await ctx.respond(embed=embed, ephemeral=True)

        log(f"Alert added by {ctx.author} in {ctx.guild}.")

    @commands.slash_command(
        name="remove-alert",
        description="Removes an alert for a keyword.",
    )
    @option(
        name="keyword",
        description="The keyword to remove.",
        autocomplete=get_keywords,
    )
    async def remove_alert(self, ctx: commands.Context, keyword: str) -> None:
        """
        It removes an alert from the database.
        
        :param ctx: commands.Context
        :type ctx: commands.Context
        :param keyword: str
        :type keyword: str
        :return: The return value is a list of tuples.
        """
        b64_keyword = b64ify(keyword)

        c = self.db.cursor()
        c.execute(
            "SELECT * FROM alerts WHERE keyword = ? AND user_id = ?",
            (b64_keyword, ctx.author.id),
        )
        if not c.fetchone():
            embed = EmbedBuilder(
                title="Error",
                description="This keyword is not in the database.",
            ).build()
            await ctx.respond(embed=embed, ephemeral=True)
            return

        c.execute(
            "DELETE FROM alerts WHERE keyword = ? AND user_id = ?",
            (b64_keyword, ctx.author.id),
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
        """
        It gets all alerts from the database and responds with a list of them
        
        :param ctx: commands.Context
        :type ctx: commands.Context
        """
        c = self.db.cursor()
        c.execute("SELECT * FROM alerts WHERE user_id = ?", (ctx.author.id,))
        alerts = c.fetchall()

        alert_list = ""
        for alert in alerts:
            alert_list += f"`{deb64ify(alert[0])}`\n"

        embed = EmbedBuilder(
            title="Alerts",
            description=alert_list,
        ).build()
        await ctx.respond(embed=embed, ephemeral=True)

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message) -> None:
        async def user_alerts() -> None:
            """
            If a message contains a keyword, send a DM to the user who added the keyword
            :return: The message.content is being returned.
            """
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
                re.search(deb64ify(keyword[0]), message.content, re.IGNORECASE)
                for keyword in keywords
            ):
                return

            # Send a DM to the user who added the alert.
            for keyword in keywords:
                if re.search(deb64ify(keyword[0]), message.content, re.IGNORECASE):
                    user = await self.bot.fetch_user(keyword[1])
                    embed = EmbedBuilder(
                        title="Alert",
                        description=f"Your keyword `{deb64ify(keyword[0])}` was mentioned in {message.channel.mention} by {message.author.mention}.",
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
            """
            It checks if a message contains any of the keywords in the list, and if it does, it sends an embed
            to a channel
            
            :param message: discord.Message
            :type message: discord.Message
            :return: The return value is a list of strings.
            """
            if (
                message.author.id == self.bot.user.id
                or message.guild.id != 238956364729155585
                or message.author.bot
                or message.author.guild.get_role(276969339901444096)
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
        """
        It sends a file to the user who called the command
        
        :param ctx: commands.Context
        :type ctx: commands.Context
        """
        await ctx.respond(
            content="Alerts Database",
            file=discord.File("util/database.sqlite"),
            ephemeral=True,
        )


def setup(bot) -> None:
    bot.add_cog(Alerts(bot))
