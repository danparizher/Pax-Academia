from __future__ import annotations

import csv
import io
import os
import subprocess
from typing import TYPE_CHECKING

import discord
from discord.commands import OptionChoice, option
from discord.ext import commands
from discord.interactions import Interaction
from file_read_backwards import FileReadBackwards

import database
from util.limiter import limit
from util.logger import log

if TYPE_CHECKING:
    from collections.abc import Iterable

    from discord.commands.context import ApplicationContext

LOADING_EMOJI = "\N{Clockwise Downwards and Upwards Open Circle Arrows}"
COMPLETED_EMOJI = "\N{White Heavy Check Mark}"
VIEW_DB_GUILD = os.getenv("GUILD_ID")
VIEW_DB_ROLE = os.getenv("ALLOW_VIEW_DATABASE_ROLE_NAME")
VIEW_LOGS_ROLE = os.getenv("ALLOW_VIEW_LOGS_ROLE_NAME")
STDOUT_LOG_FILE = os.getenv("STDOUT_LOG_FILE", "log.txt")
STDERR_LOG_FILE = os.getenv("STDERR_LOG_FILE", "log.txt")


VIEW_DB_PERMISSIONS = (
    (lambda x: x) if VIEW_DB_ROLE is None else commands.has_role(VIEW_DB_ROLE)
)
VIEW_LOGS_PERMISSIONS = (
    (lambda x: x) if VIEW_LOGS_ROLE is None else commands.has_role(VIEW_LOGS_ROLE)
)

# the order of this dictionary is very intentional
# in case multiple streams are directed to the same file
LOG_FILES = {
    STDERR_LOG_FILE: "All standard errors are redirected here.",
    "log.txt": "All logger.log() lines are saved here.",
    STDOUT_LOG_FILE: "All standard output is redirected here.",
}

GITHUB_REPO_URL = "https://github.com/danparizher/Pax-Academia"


def get_git_revision_short_hash() -> str:
    # https://stackoverflow.com/questions/14989858/get-the-current-git-hash-in-a-python-script
    return (
        subprocess.check_output(["git", "rev-parse", "--short", "HEAD"])
        .decode("ascii")
        .strip()
    )


def get_origin_revision_short_hash() -> str:
    subprocess.check_call(["git", "fetch", "origin"])
    return (
        subprocess.check_output(["git", "rev-parse", "--short", "origin/main"])
        .decode("ascii")
        .strip()
    )


def dump_tables_to_csv(tables: list[database.TableInfo]) -> Iterable[discord.File]:
    """
    It takes a list of Table objects, and returns an iterable of discord.File objects

    :param tables: list[Table]
    :type tables: list[Table]
    """
    for table in tables:
        with database.connect() as conn:
            cursor = conn.cursor()
            cursor.execute(f"SELECT * FROM {table.name}")

            with io.StringIO() as f:
                writer = csv.writer(f)
                writer.writerow(table.column_names)
                writer.writerows(cursor)
                f.seek(0)
                yield discord.File(
                    f,  # type: ignore (the class clearly accepts any readable, seekable IOBase)
                    filename=f"{table.name}.csv",
                )


class Misc(commands.Cog):
    def __init__(self: Misc, bot: commands.Bot) -> None:
        self.bot = bot

    @commands.slash_command(name="ping", description="Pings the bot.")
    @limit(3)
    async def ping(self: Misc, ctx: ApplicationContext) -> None:
        """
        It sends a message, then edits that message to say "Pong!" and the latency of the bot

        :param ctx: The context of the command
        :type ctx: commands.Context
        """
        commit = get_git_revision_short_hash()
        commit_url = f"{GITHUB_REPO_URL}/commit/{commit}"

        # Check if the commit is up-to-date
        latest_commit = get_origin_revision_short_hash()
        is_up_to_date = "Yes" if commit == latest_commit else "No"

        message = await ctx.respond("Pinging...")
        content = f"Ping: `{round(self.bot.latency * 1000)}ms`\nCommit ID: [`{commit}`](<{commit_url}>)\nIs up-to-date: `{is_up_to_date}`"

        if isinstance(message, Interaction):
            await message.edit_original_response(content=content)
        else:
            await message.edit(content=content)
        log("$ used ping", ctx.author)

    @commands.Cog.listener()
    async def on_ready(self) -> None:
        """
        The above function is a coroutine that prints a message to the console when the bot is ready
        """
        assert self.bot.user is not None
        print(f"{self.bot.user.name} has connected to Discord!")

        await self.bot.change_presence(
            activity=discord.Activity(
                name="Academic Peace...",
                type=discord.ActivityType.watching,
            ),
        )

    @VIEW_DB_PERMISSIONS
    @commands.slash_command(
        name="view-database",
        description="Download all database tables as CSV files.",
        guild_ids=None if VIEW_DB_GUILD is None else [VIEW_DB_GUILD],
        guild_only=VIEW_DB_GUILD is not None,
    )
    @limit(1)  # db access
    async def view_database(self: Misc, ctx: ApplicationContext) -> None:
        """
        It provides the database in a CSV format

        :param ctx: ApplicationContext
        :type ctx: ApplicationContext
        """
        message = await ctx.respond(f"{LOADING_EMOJI} Gathering table information...")

        async def edit(text: str) -> None:
            """
            It edits the message that the user is interacting with

            :param text: The text to send
            :type text: str
            """
            if isinstance(message, Interaction):
                await message.edit_original_response(content=text)
            else:
                await message.edit(content=text)

        log(f"$ viewed the database in {ctx.channel}, {ctx.guild}.", ctx.author)

        tables = database.grep_tables()
        await edit(f"{LOADING_EMOJI} Presented 0/{len(tables)} table(s).")

        for i, (table, file) in enumerate(
            zip(tables, dump_tables_to_csv(tables), strict=False),
        ):
            await ctx.send_followup(
                (f"Table: `{table.name}`"),
                file=file,
                ephemeral=True,
            )
            await edit(f"{LOADING_EMOJI} Presented {i + 1}/{len(tables)} table(s).")

        await edit(f"{COMPLETED_EMOJI} Presented {len(tables)} table(s).")

    @VIEW_LOGS_PERMISSIONS
    @commands.slash_command(
        name="view-logs",
        description="View the most recent logs generated by the bot.",
        guild_ids=None if VIEW_DB_GUILD is None else [VIEW_DB_GUILD],
        guild_only=VIEW_DB_GUILD is not None,
    )
    @option(
        "file",
        str,
        parameter_name="filename",
        description="The log file you want to view.",
        required=True,
        default="log.txt",
        choices=[
            OptionChoice(f"{filename} - {description}", filename)
            for filename, description in LOG_FILES.items()
        ],
    )
    @option(
        "lines",
        int,
        parameter_name="trailing_lines_count",
        description="The number of trailing lines to view.",
        required=True,
        default=20,
    )
    @limit(1)
    async def view_logs(
        self: Misc,
        ctx: ApplicationContext,
        filename: str,
        trailing_lines_count: int,
    ) -> None:
        if filename not in LOG_FILES:
            msg = f"Expected `filename` to be one of {tuple(LOG_FILES)!r} but it's actually {filename!r}"
            raise Exception(msg)

        with FileReadBackwards(filename) as log_file_backwards:
            log_lines_backwards = [
                line
                for _, line in zip(
                    range(trailing_lines_count),
                    log_file_backwards,
                    strict=False,
                )
            ]
            log_lines = reversed(log_lines_backwards)

        with io.StringIO() as f:
            f.writelines(f"{log_line}\n" for log_line in log_lines)
            f.seek(0)
            await ctx.respond(
                "Here you go!",
                file=discord.File(
                    f,  # type: ignore (the class clearly accepts any readable, seekable IOBase)
                    filename=filename,
                ),
                ephemeral=True,
            )


def setup(bot: commands.Bot) -> None:
    bot.add_cog(Misc(bot))
