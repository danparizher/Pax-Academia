from __future__ import annotations

import bisect
import os
import re
import string
import time
from dataclasses import dataclass
from hashlib import sha256
from typing import TypeAlias

import aiohttp
import discord
from discord.ext import commands, tasks

from message_formatting.embeds import EmbedBuilder
from util.logger import log

# hashlib just returns a bytes object, so this allows for slightly stricter typing
Hash: TypeAlias = bytes

MULTIPOST_EMOJI = os.getenv("MULTIPOST_EMOJI", ":regional_indicator_m:")
ALLOW_MULTIPOST_FOR_ROLE = os.getenv("ALLOW_MULTIPOST_FOR_ROLE")

# how long must you wait before being allowed to multipost
ACCEPTABLE_MULTIPOST_DELAY = 15


@dataclass
class MessageFingerprint:
    created_at: float  # unix timestamp
    author_id: int
    guild_id: int | None  # will be None for DMs
    channel_id: int
    message_id: int
    jump_url: str  # just so that we can easily refer to this message when surfacing it to humans

    attachment_urls: list[
        str
    ]  # the discord content URLs for each of the message's uploaded attachments
    cached_attachment_hashes: set[Hash] | None = (
        None  # populated on the first call to `get_attachment_hashes`
    )

    content_hash: Hash | None = (
        None  # hash of the message body, after being passed through `filter_content`
    )

    # shortcut to build a fingerprint given a message
    @classmethod
    def build(
        cls: type[MessageFingerprint],
        message: discord.Message,
    ) -> MessageFingerprint:
        filtered_content = cls.filter_content(message.content)

        return cls(
            created_at=time.time(),
            author_id=message.author.id,
            guild_id=message.guild.id if message.guild else None,
            channel_id=message.channel.id,
            message_id=message.id,
            jump_url=message.jump_url,
            attachment_urls=[attachment.url for attachment in message.attachments],
            content_hash=(
                cls.sha256_hash(filtered_content)
                if filtered_content is not None
                else None
            ),
        )

    # performs a SHA256 hash
    @staticmethod
    def sha256_hash(data: str | bytes) -> Hash:
        if isinstance(data, str):
            data = data.encode()

        return sha256(data).digest()

    # Filters message content such that it is appropriate for fingerprinting, according to these rules:
    # - Makes the string case-insensitive (via str.casefold)
    # - Removes whitespace, punctuation, and digits
    # - Returns `None` if the resulting string is less than 15 characters
    @staticmethod
    def filter_content(content: str) -> str | None:
        content = content.casefold()

        # remove all punctuation and spacing
        content = content.translate(
            str.maketrans(
                dict.fromkeys(
                    string.whitespace + string.punctuation + string.digits,
                    "",
                ),
            ),
        )

        return None if len(content) < 15 else content

    # retrieves and caches attachment hashes
    # the first call will actually download every attachment,
    # and all subsequent calls will just return the cached values
    async def get_attachment_hashes(self) -> set[Hash]:
        if self.cached_attachment_hashes is None:
            self.cached_attachment_hashes = set()

            async with aiohttp.ClientSession() as session:
                for attachment_url in self.attachment_urls[
                    :5
                ]:  # only load first 5 attachments to prevent abuse
                    try:
                        # from
                        # "https://media.discordapp.net/attachments/123/456/filename.png"
                        # to
                        # "https://media.discordapp.net/attachments/[REDACTED]/[REDACTED]/[REDACTED].png"
                        redacted_url = re.sub(
                            r"/[^/]*?\.([^\.]*)$",
                            r"/[REDACTED].\1",
                            attachment_url,
                        )
                        redacted_url = re.sub(r"\d+", r"[REDACTED]", redacted_url)

                        async with session.get(attachment_url) as resp:
                            attachment_data = await resp.read()
                    except Exception as e:
                        # it's possible that Discord may have deleted the attachment, and so we would get a 404
                        # furthermore, it's not super important that this function is 100% perfectly accurate
                        # so it's fine to just log and ignore any errors
                        log(
                            f"Error occurred while downloading attachment for message fingerprinting. Attachment URL: `{attachment_url}`, Error: {e}",
                        )
                        continue

                    self.cached_attachment_hashes.add(self.sha256_hash(attachment_data))

        return self.cached_attachment_hashes

    # returns True if two message fingerprints are similar
    # specifically, if at least one of the attachments are identical
    # or if the message body is identical and not blank
    async def matches(self: MessageFingerprint, other: MessageFingerprint) -> bool:
        # if there is content and it matches, then the fingerprint matches
        if self.content_hash is not None and (self.content_hash == other.content_hash):
            return True

        # otherwise, at least one of the attachments must match
        matching_attachments = (
            await self.get_attachment_hashes() & await other.get_attachment_hashes()
        )
        return len(matching_attachments) > 0

    # a message is a multipost of another message if both messages:
    # - were sent by the same author
    # - were sent in the same guild
    # - were sent in different channels
    # - the fingerprints match (see `matches`)
    async def is_multipost_of(
        self: MessageFingerprint,
        other: MessageFingerprint,
    ) -> bool:
        if self.author_id != other.author_id:
            return False

        if self.guild_id != other.guild_id:
            return False

        if self.channel_id == other.channel_id:
            return False

        return await self.matches(other)


class Moderation(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        # stores the fingerprints of every eligible (multipost-able)
        # message sent in the last {ACCEPTABLE_MULTIPOST_DELAY} seconds
        self.fingerprints: list[MessageFingerprint] = []
        self.clear_old_cached_data.start()

    # Records and returns a list of fingerprints that this message is a multipost of
    async def record_fingerprint(
        self: Moderation,
        message: discord.Message,
    ) -> list[MessageFingerprint]:
        fingerprint = MessageFingerprint.build(message)
        bisect.insort(self.fingerprints, fingerprint, key=lambda fp: fp.created_at)

        return [
            other_fingerprint
            for other_fingerprint in self.fingerprints
            if (
                fingerprint is not other_fingerprint
                and await fingerprint.is_multipost_of(other_fingerprint)
            )
        ]

    # deletes recorded fingerprints after {ACCEPTABLE_MULTIPOST_DELAY} seconds
    @tasks.loop(seconds=3)
    async def clear_old_cached_data(self) -> None:
        n_fingerprints_to_delete = bisect.bisect_right(
            [fp.created_at for fp in self.fingerprints],
            time.time() - ACCEPTABLE_MULTIPOST_DELAY,
        )
        del self.fingerprints[:n_fingerprints_to_delete]

    # this function should be called after every on_message
    # it will detect multiposts and will apply the following moderation:
    #   - Original Message - No action taken
    #   - Subsequent Messages - Delete the message and warn the
    #     author, then delete the warning after 15 seconds
    # A message is a "multipost" if it meets these criteria:
    #   - Author is not a bot
    #   - Author doesn't have the ALLOW_MULTIPOST_FOR_ROLE role
    #   - Message was sent in a TextChannel (not a DMChannel) that
    #     is in a CategoryChannel whose name ends with "HELP"
    #   - The same author sent another message in the last
    #     {ACCEPTABLE_MULTIPOST_DELAY} seconds with a matching
    #     fingerprint (see MessageFingerprint.matches)
    async def check_multipost(self: Moderation, message: discord.Message) -> None:
        # author not a bot
        if message.author.bot:
            return

        # author doesn't have the ALLOW_MULTIPOST_FOR_ROLE role
        if (
            isinstance(message.author, discord.Member)
            and ALLOW_MULTIPOST_FOR_ROLE is not None
            and ALLOW_MULTIPOST_FOR_ROLE.casefold()
            in (role.name.casefold() for role in message.author.roles)
        ):
            return

        # textchannel in category ending with "HELP"
        if not isinstance(message.channel, discord.TextChannel):
            return
        if (
            not message.channel.category
            or not message.channel.category.name.lower().endswith("help")
        ):
            return

        previous_postings = await self.record_fingerprint(message)

        if not previous_postings:
            # This is a new, unique message. Not a multipost.
            return

        first_post = previous_postings[0]

        embed = EmbedBuilder(
            title="Multi-Post Deleted",
            description=(
                "Please don't send the same message in multiple channels."
                " Your message has been deleted."
                " You may delete your original message to re-post it elsewhere."
                " \n\nThis warning will be deleted in 15 seconds."
            ),
            fields=[
                (
                    "Original Message",
                    f"[link]({first_post.jump_url})",
                    True,
                ),
            ],
        ).build()

        try:
            await message.reply(
                message.author.mention,
                embed=embed,
                delete_after=15,
            )
            await message.delete()
            log(
                f"Deleted multi-posted message (id: {message.id}) from $ in #{message.channel.name}",
                message.author,
            )
        except discord.errors.HTTPException as e:
            if "unknown message".casefold() in repr(e).casefold():
                # The multiposted message has already been deleted, take no action
                return
            # unknown error, just raise it
            raise

    @commands.Cog.listener()
    async def on_message(self: Moderation, message: discord.Message) -> None:
        await self.check_multipost(message)

    @commands.Cog.listener()
    async def on_raw_message_delete(
        self: Moderation,
        payload: discord.RawMessageDeleteEvent,
    ) -> None:
        # You're allowed to re-post messages that have been deleted.
        for i, fingerprint in enumerate(self.fingerprints):
            if payload.message_id == fingerprint.message_id:
                del self.fingerprints[i]
                break


def setup(bot: commands.Bot) -> None:
    bot.add_cog(Moderation(bot))
