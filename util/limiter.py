from __future__ import annotations

import functools
from typing import Awaitable, Callable, ParamSpec, TypeVar

from discord import ApplicationContext

import database
from message_formatting.embeds import EmbedBuilder
from util.logger import log

LimitedCommandParams = ParamSpec("LimitedCommandParams")
LimitedCommandReturnValue = TypeVar("LimitedCommandReturnValue")


def limit(
    limit_level_requirement: int,  # users at this `limitLevel` or higher are banned from using the command
) -> Callable[
    [Callable[LimitedCommandParams, Awaitable[LimitedCommandReturnValue]]],
    Callable[LimitedCommandParams, Awaitable[LimitedCommandReturnValue | None]],
]:
    """
    ! This decorator only works on slash commands. !
    Limit levels:
    None: No limit
    1: Cannot use database commands (I.e alerts & applications)
    2: Cannot use pax non help specific commands (I.e. chemsearch, define, wiki, ...)
    3: Cannot use pax. (ping, rule, tip...)
    Levels are inclusive, so if you are level 2, you cannot use level 1 commands either.
    """

    def decorator(
        func: Callable[LimitedCommandParams, Awaitable[LimitedCommandReturnValue]],
    ) -> Callable[LimitedCommandParams, Awaitable[LimitedCommandReturnValue | None]]:
        @functools.wraps(func)
        async def wrapper(
            *args: LimitedCommandParams.args,
            **kwargs: LimitedCommandParams.kwargs,
        ) -> LimitedCommandReturnValue | None:
            """
            Wrapper to determine if the user is limited or not.
            """

            ctx = None
            for arg in args:
                if isinstance(arg, ApplicationContext):
                    ctx = arg
                    break

            if ctx is None:
                log(
                    f"@limit() decorator was applied to non-slash-command {func!r}! "
                    "Permitting function call without checking permissions!",
                )
                return await func(*args, **kwargs)

            conn = database.connect()
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
                limit_level = 0
                conn.commit()
            else:
                limit_level = limit_level[0] or 0

            if limit_level >= limit_level_requirement:
                embed = EmbedBuilder(
                    title="You cannot use this command!",
                    description="You are limited from using this command! Please contact a moderator if you believe this is a mistake.",
                    color=0xFF0000,
                ).build()
                await ctx.respond(embed=embed, ephemeral=True)
                log(
                    f"$ tried to use {ctx.command.name}. But is limited from using it.",
                    ctx.author,
                )
                return None

            return await func(*args, **kwargs)

        return wrapper

    return decorator
