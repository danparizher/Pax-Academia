import contextlib
import re
import sqlite3

import discord
from discord.commands import option
from discord.commands.context import ApplicationContext
from discord.ext import commands

from util.EmbedBuilder import EmbedBuilder
from util.Logging import Log, limit


def get_keywords(ctx: discord.AutocompleteContext) -> list[str]:
    """
    It gets all the keywords from the database for the user who is currently using the command

    :param ctx: discord.AutocompleteContext
    :type ctx: discord.AutocompleteContext
    :return: A list of keywords that the user has set up for alerts.
    """

    if not ctx.interaction.user:
        return []

    # We no longer keep track of the name because this can change, breaking the alert.
    conn = sqlite3.connect("util/database.sqlite")
    data = [
        keyword
        for (keyword,) in conn.cursor()
        .execute("SELECT message FROM alert WHERE uid = ?", (ctx.interaction.user.id,))
        .fetchall()
    ]
    conn.close()
    return data


class Alerts(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.db = sqlite3.connect("util/database.sqlite")

    # Allows the user to enter a keyword to be alerted when it is mentioned in the guild. When the keyword is used, the bot will send a DM to the user.
    @commands.slash_command(
        name="alerts-add",
        description="Adds an alert for a keyword.",
    )
    @limit(1)
    async def add_alert(self, ctx: ApplicationContext, keyword: str) -> None:
        """
        Checks if the keyword is already in the database, if it is, sends an error message, if it
        isn't, adds the keyword to the database and sends a success message.
        Properly escapes invalid regex.

        :param ctx: ApplicationContext
        :type ctx: ApplicationContext
        :param keyword: str
        :type keyword: str
        :return: The return type is None.
        """

        try:
            re.compile(keyword)
            escaped = False
        except re.error:
            keyword = re.escape(keyword)
            escaped = True

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
            description=f"Added alert for keyword `{keyword}`."
            + (
                "\nNote: the input was not valid regex, so special characters have been escaped."
                if escaped
                else ""
            ),
        ).build()
        await ctx.respond(embed=embed, ephemeral=True)

        Log(f"Alert added by $ in {ctx.guild}.", ctx.author)

    @commands.slash_command(
        name="alerts-remove",
        description="Removes an alert for a keyword.",
    )
    @option(
        name="keyword",
        description="The keyword to remove.",
        autocomplete=get_keywords,
    )
    @limit(1)
    async def remove_alert(self, ctx: ApplicationContext, keyword: str) -> None:
        """
        It removes an alert from the database.

        :param ctx: ApplicationContext
        :type ctx: ApplicationContext
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

        Log(f"Alert removed by $ in {ctx.guild}.", ctx.author)

    @commands.slash_command(name="alerts-list", description="Lists all alerts.")
    @limit(3)
    # User should still be allowed to remove their alerts if they have too many
    async def list_alerts(self, ctx: ApplicationContext) -> None:
        """
        It gets all alerts from the database and responds with a list of them

        :param ctx: ApplicationContext
        :type ctx: ApplicationContext
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

    @commands.slash_command(name="alerts-clear", description="Clears all alerts.")
    async def clear_alerts(self, ctx: ApplicationContext) -> None:
        """
        It clears all alerts from the database.

        :param ctx: ApplicationContext
        :type ctx: ApplicationContext
        """
        c = self.db.cursor()
        c.execute("DELETE FROM alert WHERE uid = ?", (ctx.author.id,))
        self.db.commit()

        embed = EmbedBuilder(
            title="Success",
            description="Cleared all alerts.",
        ).build()
        await ctx.respond(embed=embed, ephemeral=True)

        Log(f"Alerts cleared by $ in {ctx.guild}.", ctx.author)

    @commands.slash_command(
        name="alerts-pause",
        description="Pauses alerts.",
    )
    async def pause_alerts(self, ctx: ApplicationContext) -> None:
        """
        It pauses alerts for the user who is currently using the command.

        :param ctx: ApplicationContext
        :type ctx: ApplicationContext
        """
        c = self.db.cursor()
        c.execute(
            "UPDATE alert SET paused = 1 WHERE uid = ?",
            (ctx.author.id,),
        )
        self.db.commit()

        c.execute("SELECT * FROM alert WHERE uid = ? AND paused = 1", (ctx.author.id,))
        if c.fetchone():
            embed = EmbedBuilder(
                title="Error",
                description="Alerts are already paused.",
            ).build()
            await ctx.respond(embed=embed, ephemeral=True)
            return

        embed = EmbedBuilder(
            title="Success",
            description="Paused alerts.",
        ).build()
        await ctx.respond(embed=embed, ephemeral=True)

        Log(f"Alerts paused by $ in {ctx.guild}.", ctx.author)

    @commands.slash_command(
        name="alerts-resume",
        description="Resumes alerts.",
    )
    async def resume_alerts(self, ctx: ApplicationContext) -> None:
        """
        It resumes alerts for the user who is currently using the command.

        :param ctx: ApplicationContext
        :type ctx: ApplicationContext
        """
        c = self.db.cursor()
        c.execute(
            "UPDATE alert SET paused = 0 WHERE uid = ?",
            (ctx.author.id,),
        )
        self.db.commit()

        c.execute("SELECT * FROM alert WHERE uid = ? AND paused = 0", (ctx.author.id,))
        if c.fetchone():
            embed = EmbedBuilder(
                title="Error",
                description="Alerts are already resumed.",
            ).build()
            await ctx.respond(embed=embed, ephemeral=True)
            return

        embed = EmbedBuilder(
            title="Success",
            description="Resumed alerts.",
        ).build()
        await ctx.respond(embed=embed, ephemeral=True)

        Log(f"Alerts resumed by $ in {ctx.guild}.", ctx.author)

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message) -> None:
        async def user_alerts() -> None:
            """
            If a message contains a keyword, send a DM to the user who added the keyword
            :return: The message.content is being returned.
            """
            assert (
                self.bot.user is not None
            ), "on_message only fires when the bot is already logged in"

            # do not process alerts for bot messages or in DMs
            if message.author.bot or isinstance(message.author, discord.User):
                return

            # Should be impossible (since we already checked if this is a DM)
            # this is just to satisfy type-checkers
            if message.channel not in message.author.guild.channels:
                return

            # if the users alerts are paused, don't send them
            c = self.db.cursor()
            c.execute(
                "SELECT * FROM alert WHERE uid = ? AND paused = 0",
                (message.author.id,),
            )
            alerts = c.fetchall()
            if not alerts:
                return

            c = self.db.cursor()
            c.execute("SELECT message, uid FROM alert")

            for keyword, uid in c.fetchall():
                if not re.search(keyword, message.content, re.IGNORECASE):
                    continue

                # try to pull from cache, otherwise re-fetch
                member = message.channel.guild.get_member(uid)
                if not member:
                    try:
                        member = await message.channel.guild.fetch_member(uid)
                    except discord.NotFound:
                        continue

                if not message.channel.permissions_for(member).view_channel:
                    continue

                embed = EmbedBuilder(
                    title="Alert",
                    description=f"Your keyword `{keyword}` was mentioned in {message.channel.mention} by {message.author.mention}.",
                    fields=[
                        ("Message", message.content, False),
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


def setup(bot: commands.Bot) -> None:
    bot.add_cog(Alerts(bot))
