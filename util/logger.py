# !SKA#0001 24/10/2022

import datetime
import re
from pathlib import Path

import discord


def log(message: str, user: discord.User | None = None) -> None:
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
