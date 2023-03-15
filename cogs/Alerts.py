import contextlib
import re
import sqlite3

import discord
from discord.commands import option
from discord.ext import commands

from util.EmbedBuilder import EmbedBuilder
from util.Logging import Log


def get_keywords(ctx: discord.AutocompleteContext) -> list:
    """
    It gets all the keywords from the database for the user who is currently using the command

    :param ctx: discord.AutocompleteContext
    :type ctx: discord.AutocompleteContext
    :return: A list of keywords that the user has set up for alerts.
    """

    # We no longer keep track of the name because this can change, breaking the alert.
    conn = sqlite3.connect("util/database.sqlite")
    data = [
        keyword[0]
        for keyword in conn.cursor()
        .execute("SELECT message FROM alert WHERE uid = ?", (ctx.interaction.user.id,))
        .fetchall()
    ]
    conn.close()
    return data


class Alerts(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.db = sqlite3.connect("util/database.sqlite")
        c = self.db.cursor()

    # Allows the user to enter a keyword to be alerted when it is mentioned in the guild. When the keyword is used, the bot will send a DM to the user.
    @commands.slash_command(
        name="alerts-add", description="Adds an alert for a keyword."
    )
    async def add_alert(self, ctx: commands.Context, keyword: str) -> None:
        """
        Checks if the keyword is already in the database, if it is, sends an error message, if it
        isn't, adds the keyword to the database and sends a success message.

        :param ctx: commands.Context
        :type ctx: commands.Context
        :param keyword: str
        :type keyword: str
        :return: The return type is None.
        """

        c = self.db.cursor()
        c.execute(
            "SELECT * FROM alert WHERE message = ? AND uid = ?",
            (keyword, ctx.author.id),
        )
        if c.fetchone():
            embed = EmbedBuilder(
                title="Error",
                description="This keyword is already in the database.",
            ).build()
            await ctx.respond(embed=embed, ephemeral=True)
            return

        c.execute(
            "INSERT INTO alert(uid, message) VALUES (?, ?)",
            (ctx.author.id, keyword),
        )
        self.db.commit()

        embed = EmbedBuilder(
            title="Success",
            description=f"Added alert for keyword `{keyword}`.",
        ).build()
        await ctx.respond(embed=embed, ephemeral=True)

        Log(f"Alert added by {ctx.author} in {ctx.guild}.")

    @commands.slash_command(
        name="alerts-remove",
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
        """

        c = self.db.cursor()
        c.execute(
            "SELECT * FROM alert WHERE message = ? AND uid = ?",
            (keyword, ctx.author.id),
        )
        if not c.fetchone():
            embed = EmbedBuilder(
                title="Error",
                description="This keyword is not in the database.",
            ).build()
            await ctx.respond(embed=embed, ephemeral=True)
            return

        c.execute(
            "DELETE FROM alert WHERE message = ? AND uid = ?",
            (keyword, ctx.author.id),
        )
        self.db.commit()

        embed = EmbedBuilder(
            title="Success",
            description=f"Removed alert for keyword `{keyword}`.",
        ).build()
        await ctx.respond(embed=embed, ephemeral=True)

        Log(f"Alert removed by {ctx.author} in {ctx.guild}.")

    @commands.slash_command(name="alerts-list", description="Lists all alerts.")
    async def list_alerts(self, ctx: commands.Context) -> None:
        """
        It gets all alerts from the database and responds with a list of them

        :param ctx: commands.Context
        :type ctx: commands.Context
        """
        c = self.db.cursor()
        c.execute("SELECT * FROM alert WHERE uid = ?", (ctx.author.id,))
        alerts = c.fetchall()

        alert_list = "".join(f"`{alert[2]}`\n" for alert in alerts)
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
            c.execute("SELECT * FROM alert")
            keywords = c.fetchall()
            if not any(
                re.search(keyword[2], message.content, re.IGNORECASE)
                for keyword in keywords
            ):
                return

            # Send a DM to the user who added the alert.
            for keyword in keywords:
                if re.search(keyword[2], message.content, re.IGNORECASE):
                    try:
                        member = await message.channel.guild.fetch_member(keyword[1])
                    except discord.NotFound:
                        return
                    if not message.channel.permissions_for(member).view_channel:
                        return
                    embed = EmbedBuilder(
                        title="Alert",
                        description=f"Your keyword `{keyword[2]}` was mentioned in {message.channel.mention} by {message.author.mention}.",
                        fields=[
                            ("Message", message.content[:1024], False),
                            (
                                "Message Link",
                                f"[Click to see message]({message.jump_url})",
                                False,
                            ),
                        ],
                    ).build()
                    with contextlib.suppress(discord.Forbidden):
                        await member.send(embed=embed)

        await user_alerts()


def setup(bot) -> None:
    bot.add_cog(Alerts(bot))
