from __future__ import annotations

import asyncio
import re
from contextlib import suppress
from dataclasses import dataclass
from time import perf_counter
from typing import TYPE_CHECKING

import discord
from discord.commands import option
from discord.ext import commands, tasks

import database
from message_formatting.embeds import EmbedBuilder
from util.limiter import limit, server
from util.logger import log

if TYPE_CHECKING:
    from discord.commands.context import ApplicationContext


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
    conn = database.connect()
    data = [
        keyword
        for (keyword,) in conn.cursor()
        .execute("SELECT message FROM alert WHERE uid = ?", (ctx.interaction.user.id,))
        .fetchall()
    ]
    conn.close()
    return data


@dataclass
class AlertRecord:
    """
    Represents an alert that was sent to a user.
    We keep track of these to avoid duplicate alerts.
    They have an expiry time to avoid unnecessary memory usage.
    """

    message_id: int
    alerted_user_id: int
    expires_at: float = 0

    def expire_in(self, seconds: float) -> AlertRecord:
        self.expires_at = perf_counter() + seconds
        return self

    @property
    def expired(self) -> bool:
        return perf_counter() > self.expires_at

    def __hash__(self) -> int:
        return hash((self.message_id, self.alerted_user_id))

    def __eq__(self, other: AlertRecord) -> bool:
        return (
            self.message_id == other.message_id
            and self.alerted_user_id == other.alerted_user_id
        )


class Alerts(commands.Cog):
    ALERT_MEMORY_DURATION = 60 * 60 * 6  # 6 hours

    def __init__(self: Alerts, bot: commands.Bot) -> None:
        self.bot = bot
        self.db = database.connect()
        self.alert_memory: set[AlertRecord] = set()

    # periodically clear expired alert records
    @tasks.loop(seconds=15)
    async def clean_alert_memory(self) -> None:
        for record in self.alert_memory.copy():
            if record.expired:
                self.alert_memory.remove(record)

    # Allows the user to enter a keyword to be alerted when it is mentioned in the guild. When the keyword is used, the bot will send a DM to the user.
    @commands.slash_command(
        name="alerts-add",
        description="Adds an alert for a keyword.",
    )
    @option(
        "keyword",
        str,
        description="The keyword to be alerted on. Regex is supported.",
        required=True,
    )
    @limit(1)
    @server
    async def add_alert(self: Alerts, ctx: ApplicationContext, keyword: str) -> None:
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

        log(f"Alert added by $ in {ctx.guild}.", ctx.author)

    @commands.slash_command(
        name="alerts-remove",
        description="Removes an alert for a keyword.",
    )
    @option(
        "keyword",
        str,
        description="The keyword to remove.",
        autocomplete=get_keywords,
    )
    @limit(1)
    @server
    async def remove_alert(self: Alerts, ctx: ApplicationContext, keyword: str) -> None:
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

        log(f"Alert removed by $ in {ctx.guild}.", ctx.author)

    @commands.slash_command(name="alerts-list", description="Lists all alerts.")
    # User should still be allowed to remove their alerts if they have too many
    @limit(3)
    @server
    async def list_alerts(self: Alerts, ctx: ApplicationContext) -> None:
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
    @limit(3)
    @server
    async def clear_alerts(self: Alerts, ctx: ApplicationContext) -> None:
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

        log(f"Alerts cleared by $ in {ctx.guild}.", ctx.author)

    @commands.slash_command(
        name="alerts-pause",
        description="Pauses alerts.",
    )
    @limit(1)
    @server
    async def pause_alerts(self: Alerts, ctx: ApplicationContext) -> None:
        """
        It pauses alerts for the user who is currently using the command.

        :param ctx: ApplicationContext
        :type ctx: ApplicationContext
        """
        c = self.db.cursor()
        c.execute(
            "UPDATE alert SET paused = TRUE WHERE uid = ?",
            (ctx.author.id,),
        )
        self.db.commit()

        embed = EmbedBuilder(
            title="Success",
            description="Paused alerts.",
        ).build()

        await ctx.respond(embed=embed, ephemeral=True)

        log(f"Alerts paused by $ in {ctx.guild}.", ctx.author)

    @commands.slash_command(
        name="alerts-resume",
        description="Resumes alerts.",
    )
    @limit(1)
    @server
    async def resume_alerts(self: Alerts, ctx: ApplicationContext) -> None:
        """
        It resumes alerts for the user who is currently using the command.

        :param ctx: ApplicationContext
        :type ctx: ApplicationContext
        """
        c = self.db.cursor()
        c.execute(
            "UPDATE alert SET paused = FALSE WHERE uid = ?",
            (ctx.author.id,),
        )
        self.db.commit()

        embed = EmbedBuilder(
            title="Success",
            description="Resumed alerts.",
        ).build()
        await ctx.respond(embed=embed, ephemeral=True)

        log(f"Alerts resumed by $ in {ctx.guild}.", ctx.author)

    @staticmethod
    async def get_or_fetch_member(
        guild: discord.Guild,
        member_id: int,
    ) -> discord.Member | None:
        try:
            return guild.get_member(member_id) or await guild.fetch_member(member_id)
        except discord.NotFound:
            return None

    async def send_and_record_alert(
        self: Alerts,
        embed: discord.Embed,
        send_to: discord.Member,
        message_id: int,
    ) -> None:
        alert_record = AlertRecord(message_id, send_to.id).expire_in(
            self.ALERT_MEMORY_DURATION,
        )
        if alert_record in self.alert_memory:
            # we already alerted this user, don't send it again
            return

        # immediately record the alert, to act as a debounce
        # then, if failure ensues, remove it afterwards
        self.alert_memory.add(alert_record)
        with suppress(discord.Forbidden):
            try:
                await send_to.send(embed=embed)
            except:
                self.alert_memory.remove(alert_record)
                raise

    async def maybe_send_alerts(self: Alerts, message: discord.Message) -> None:
        """
        If the message is valid and contains keyword(s),
        send DM(s) to the user(s) who added the keyword(s)
        """

        # never alert on bot messages
        if message.author.bot:
            return

        # filter out bad channel types
        if isinstance(
            message.channel,
            (
                # we need the channel to be loaded correctly
                discord.PartialMessageable,
                # do not alert from DM's
                discord.DMChannel,
                discord.GroupChannel,
            ),
        ):
            return

        c = self.db.cursor()
        c.execute(
            "SELECT message, uid FROM alert WHERE (paused = FALSE OR paused IS NULL)",
        )

        # group together alerts by the person who is to be alerted
        # (so that we don't alert someone multiple times for the same message)
        alerts: dict[int, list[str]] = {}
        for keyword, uid in c.fetchall():
            if not re.search(keyword, message.content, re.IGNORECASE):
                continue

            member = await self.get_or_fetch_member(message.channel.guild, uid)
            if not member or not message.channel.permissions_for(member).view_channel:
                continue

            alerts.setdefault(uid, [])
            alerts[uid].append(keyword)

        # send the alerts
        sending_alerts = []
        for uid, keywords in alerts.items():
            member = await self.get_or_fetch_member(message.channel.guild, uid)
            if member is None:
                continue

            embed = EmbedBuilder(
                title="Alert",
                description=(
                    f"Your {'keyword' if len(keywords) == 1 else 'keywords'} "
                    f"{', '.join([f'`{keyword}`' for keyword in keywords])} was mentioned "
                    f"in {message.channel.mention} by {message.author.mention}."
                ),
                fields=[
                    ("Message", message.content, False),
                    (
                        "Message Link",
                        f"[Click to see message]({message.jump_url})",
                        False,
                    ),
                ],
            ).build()

            sending_alerts.append(self.send_and_record_alert(embed, member, message.id))

        await asyncio.gather(*sending_alerts)

    @commands.Cog.listener()
    async def on_message(self: Alerts, message: discord.Message) -> None:
        await self.maybe_send_alerts(message)

    @commands.Cog.listener()
    async def on_raw_message_edit(
        self: Alerts,
        payload: discord.RawMessageUpdateEvent,
    ) -> None:
        channel = self.bot.get_channel(
            payload.channel_id,
        ) or await self.bot.fetch_channel(
            payload.channel_id,
        )

        assert isinstance(
            channel,
            discord.abc.Messageable,
        ), "Presumably a channel that has messages in it should be 'messageable'."

        message = await channel.fetch_message(payload.message_id)
        await self.maybe_send_alerts(message)


def setup(bot: commands.Bot) -> None:
    bot.add_cog(Alerts(bot))
