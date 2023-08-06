import csv
import io
import os
import sqlite3
from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path

import discord
from discord.commands.context import ApplicationContext
from discord.ext import commands
from discord.interactions import Interaction

from util.Logging import Log, limit

DATABASE_FILES = [
    "util/database.sqlite",
    "log.txt",
]
LOADING_EMOJI = "\N{Clockwise Downwards and Upwards Open Circle Arrows}"
COMPLETED_EMOJI = "\N{White Heavy Check Mark}"
VIEW_DB_GUILD = os.getenv("ALLOW_VIEW_DATABASE_GUILD_ID")
VIEW_DB_ROLE = os.getenv("ALLOW_VIEW_DATABASE_ROLE_NAME")

VIEW_DB_PERMISSIONS = (
    (lambda x: x) if VIEW_DB_ROLE is None else commands.has_role(VIEW_DB_ROLE)
)


@dataclass
class Table:
    database_file_path: str
    database_name: str
    name: str
    column_names: list[str]


def grep_tables() -> list[Table]:
    """
    It returns a list of Table objects, each of which contains the path to a database file, the name of
    the database, the name of a table in the database, and a list of the column names in the table
    :return: A list of Table objects.
    """
    tables: list[Table] = []
    for database_file in DATABASE_FILES:
        database_name = Path(database_file).name
        if database_file.endswith(".txt"):
            tables.append(
                Table(
                    database_file_path=database_file,
                    database_name=database_name,
                    name=database_name,
                    column_names=["log"],
                ),
            )
            continue

        with sqlite3.connect(database_file) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT
                    name
                FROM
                    sqlite_schema
                WHERE
                    type ='table'
                    AND
                    name NOT LIKE 'sqlite_%'
                """,
            )

            for (table_name,) in cursor.fetchall():
                cursor.execute(f"PRAGMA table_info({table_name})")
                tables.append(
                    Table(
                        database_file_path=database_file,
                        database_name=database_name,
                        name=table_name,
                        column_names=[x[1] for x in cursor.fetchall()],
                    ),
                )
    return tables


def dump_tables_to_csv(tables: list[Table]) -> Iterable[discord.File]:
    """
    It takes a list of Table objects, and returns an iterable of discord.File objects

    :param tables: list[Table]
    :type tables: list[Table]
    """
    for table in tables:
        if table.database_file_path.endswith(".txt"):
            yield discord.File(table.database_file_path)
            continue

        with sqlite3.connect(table.database_file_path) as conn:
            cursor = conn.cursor()
            cursor.execute(f"SELECT * FROM {table.name}")

            with io.StringIO() as f:
                writer = csv.writer(f)
                writer.writerow(table.column_names)
                writer.writerows(cursor.fetchall())
                f.seek(0)
                yield discord.File(
                    f,
                    filename=f"{table.database_name}.{table.name}.csv",
                )


class Misc(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @commands.slash_command(name="ping", description="Pings the bot.")
    @limit(3)
    async def ping(self, ctx: ApplicationContext) -> None:
        """
        It sends a message, then edits that message to say "Pong!" and the latency of the bot

        :param ctx: The context of the command
        :type ctx: commands.Context
        """
        message = await ctx.respond("Pinging...")
        content = f"Pong! {round(self.bot.latency * 1000)}ms"

        if isinstance(message, Interaction):
            await message.edit_original_response(content=content)
        else:
            await message.edit(content=content)
        Log("$ used ping", ctx.author)

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
    async def view_database(self, ctx: ApplicationContext) -> None:
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

        Log(f"$ viewed the database in {ctx.channel}, {ctx.guild}.", ctx.author)

        tables = grep_tables()
        await edit(f"{LOADING_EMOJI} Presented 0/{len(tables)} table(s).")

        for i, (table, file) in enumerate(
            zip(tables, dump_tables_to_csv(tables), strict=False),
        ):
            await ctx.send_followup(
                (f"Database: `{table.database_file_path}`\nTable: `{table.name}`"),
                file=file,
                ephemeral=True,
            )
            await edit(f"{LOADING_EMOJI} Presented {i + 1}/{len(tables)} table(s).")

        await edit(f"{COMPLETED_EMOJI} Presented {len(tables)} table(s).")


def setup(bot: commands.Bot) -> None:
    bot.add_cog(Misc(bot))
