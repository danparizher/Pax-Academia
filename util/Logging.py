# !SKA#0001 24/10/2022

import datetime
import functools
import re
import sqlite3
from pathlib import Path
from typing import Awaitable, Callable, ParamSpec, TypeAlias, TypeVar

import discord

from util.embed_builder import EmbedBuilder

LimitedCommandParams = ParamSpec("LimitedCommandParams")
LimitedCommandReturnValue = TypeVar("LimitedCommandReturnValue")


def limit(
    minimum_limit_level: int,  # the minimum `limitLevel` required to use the command
) -> Callable[
    [Callable[LimitedCommandParams, Awaitable[LimitedCommandReturnValue]]],
    Callable[LimitedCommandParams, Awaitable[LimitedCommandReturnValue | None]],
]:
    """
    Limit levels:
    None: No limit
    1: Cannot use database commands (I.e alerts & applications)
    2: Cannot use pax non help specific commands (I.e. chemsearch, define, wiki, ...)
    3: Cannot use pax. (ping, rule, tip...)
    Levels are inclusive, so if you are level 2, you cannot use level 1 commands either.
    """

    def decorator(
        func: Callable[LimitedCommandParams, Awaitable[LimitedCommandReturnValue]]
    ) -> Callable[LimitedCommandParams, Awaitable[LimitedCommandReturnValue | None]]:
        @functools.wraps(func)
        async def wrapper(
            *args: LimitedCommandParams.args, **kwargs: LimitedCommandParams.kwargs
        ) -> LimitedCommandReturnValue | None:
            """
            Wrapper to determine if the user is limited or not.
            """

            ctx = None
            for arg in args:
                if isinstance(arg, discord.ApplicationContext):
                    ctx = arg
                    break

            if not ctx or not ctx.author or not ctx.author.id:
                # in order to actually do any limiting, we need to know who used the command
                Log(
                    f"@limit({minimum_limit_level}) is BROKEN for {func!r}. Failed to find an author!"
                )
                return await func(*args, **kwargs)

            conn = sqlite3.connect("util/database.sqlite")
            c = conn.cursor()
            limit_level = c.execute(
                "SELECT limitLevel from user where uid = ?",
                (ctx.author.id,),
            ).fetchone()

            if limit_level is None:  # User DOES NOT exist in database, add them.
                c.execute(
                    "INSERT INTO user VALUES (?, ?, ?, ?, ?, ?)",
                    (ctx.author.id, 0, False, None, 0, None),
                )  # See ERD.mdj
                limit_level = float("inf")
                conn.commit()
            else:
                limit_level = limit_level[0] or float("inf")

            if limit_level >= minimum_limit_level:
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
    def __init__(
        self, message: str, user: discord.User | discord.Member | None = None
    ) -> None:
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
