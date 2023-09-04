from __future__ import annotations

import functools
from typing import Awaitable, Callable, ParamSpec, TypeVar
from os import getenv

from discord import ApplicationContext

import database
from message_formatting.embeds import EmbedBuilder
from util.logger import log

LimitedCommandParams = ParamSpec("LimitedCommandParams")
LimitedCommandReturnValue = TypeVar("LimitedCommandReturnValue")

GUILD_ID = int(getenv("GUILD_ID", "-1"))
assert GUILD_ID != -1, "GUILD_ID is not set in .env"

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



def server(
    func: Callable[LimitedCommandParams, Awaitable[LimitedCommandReturnValue]],
) -> Callable[LimitedCommandParams, Awaitable[LimitedCommandReturnValue | None]]:
    """
    ! This decorator only works on slash commands. !
    use @server to wrap a slash command to make sure it is only used in the correct guild.
    """
    @functools.wraps(func)
    async def wrapper(
        *args: LimitedCommandParams.args,
        **kwargs: LimitedCommandParams.kwargs,
    ) -> LimitedCommandReturnValue | None:
        """
        Wrapper to determine if the command is used in the correct guild.
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
        
        used_guild_id = ctx.guild_id
        if used_guild_id is None:
            log(
                f"$ tried to use {ctx.command.name}. But is not in a guild.",
                ctx.author,
            )
            await ctx.respond("Sorry, you cannot use this command in dms.", ephemeral=True)
            return None
        elif used_guild_id != GUILD_ID: # This should not happen as the bot should only be in one guild.
            log(
                f"$ tried to use {ctx.command.name}. But is not in the correct guild.",
                ctx.author,
            )
            await ctx.respond("Sorry, you cannot use this command in this guild.", ephemeral=True)
            return None
        
        return await func(*args, **kwargs)

    return wrapper

