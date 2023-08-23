# !SKA#0001 24/10/2022

import datetime
import functools
import re
from pathlib import Path

import discord

import database
from util.embed_builder import EmbedBuilder


def limit(_limit_level: int) -> callable:
    """
    Limit levels:
    None: No limit
    1: Cannot use database commands (I.e alerts & applications)
    2: Cannot use pax non help specific commands (I.e. chemsearch, define, wiki, ...)
    3: Cannot use pax. (ping, rule, tip...)
    Levels are inclusive, so if you are level 2, you cannot use level 1 commands either.
    """

    def decorator(func: callable) -> callable:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs) -> callable:
            """
            Wrapper to determine if the user is limited or not.
            """

            # Get the author id
            author_id = None
            for arg in args:
                try:
                    author_id = arg.author.id
                    ctx = arg
                except AttributeError:  # Type is not a context
                    continue

            if (
                author_id is not None
            ):  # if no author exists, then we cannot limit, return func instead
                conn = database.connect()
                c = conn.cursor()
                limit_level = c.execute(
                    "SELECT limitLevel from user where uid = ?",
                    (author_id,),
                ).fetchone()

                if limit_level is None:  # User DOES NOT exist in database, add them.
                    c.execute(
                        "INSERT INTO user VALUES (?, ?, ?, ?, ?, ?)",
                        (author_id, 0, False, None, 0, None),
                    )  # See ERD.mdj
                    limit_level = 0
                    conn.commit()
                else:
                    limit_level = limit_level[0] or 0

                if limit_level >= _limit_level:
                    embed = EmbedBuilder(
                        title="You cannot use this command!",
                        description="You are limited from using this command! Please contact a moderator if you believe this is a mistake.",
                        color=0xFF0000,
                    ).build()
                    await ctx.respond(embed=embed, ephemeral=True)
                    Log(
                        f"$ tried to use {ctx.command.name}. But is limited from using it.",
                        ctx.author,
                    )
                    return None

            return await func(*args, **kwargs)

        return wrapper

    return decorator


class Log:
    def __init__(self, message: str, user: discord.User | None = None) -> None:
        """
        Basic logging module.
        If a message and a user is given, Will replace $ in message with the user's name,
        depending on whether it is an old or new username.
        If no user given, will just log the message.
        """
        with Path("log.txt").open("a", encoding="utf-8") as log_file:
            # get current time
            now = datetime.datetime.now(tz=datetime.timezone.utc)
            now_str: str = now.strftime("%Y-%m-%d %H:%M:%S")

            # Check if user is given
            if user is not None:
                if str(user.discriminator) == "0":
                    user_name = f"@{user.name}"
                else:
                    user_name = f"{user.name}#{user.discriminator}"

                message = re.sub(
                    r"(?<!\/)\$",
                    user_name,
                    message,
                )  # replaces $ in string to new username

            log_file.write(f"{now_str} - {message}\n")
