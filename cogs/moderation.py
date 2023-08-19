import os
import re
import string
import time
from dataclasses import dataclass
from hashlib import sha256
from typing import Annotated, TypeAlias

import aiohttp
import discord
from discord.ext import commands, tasks

from message_formatting.embeds import EmbedBuilder
from util.logger import log

# hashlib just returns a bytes object, so this allows for slightly stricter typing
Hash: TypeAlias = bytes

MULTIPOST_EMOJI = os.getenv("MULTIPOST_EMOJI", ":regional_indicator_m:")
ALLOW_MULTIPOST_FOR_ROLE = os.getenv("ALLOW_MULTIPOST_FOR_ROLE")


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
    cached_attachment_hashes: set[
        Hash
    ] | None = None  # populated on the first call to `get_attachment_hashes`

    content_hash: Hash | None = (
        None  # hash of the message body, after being passed through `filter_content`
    )

    # shortcut to build a fingerprint given a message
    @classmethod
    def build(
        cls: type["MessageFingerprint"],
        message: discord.Message,
    ) -> "MessageFingerprint":
        filtered_content = cls.filter_content(message.content)

        return cls(
            created_at=time.time(),
            author_id=message.author.id,
            guild_id=message.guild.id if message.guild else None,
            channel_id=message.channel.id,
            message_id=message.id,
            jump_url=message.jump_url,
            attachment_urls=[attachment.url for attachment in message.attachments],
            content_hash=cls.hash(filtered_content)
            if filtered_content is not None
            else None,
        )

    # performs a SHA256 hash
    @staticmethod
    def hash(data: str | bytes) -> Hash:
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
                {
                    unwanted_character: ""
                    for unwanted_character in (
                        string.whitespace + string.punctuation + string.digits
                    )
                },
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

                    self.cached_attachment_hashes.add(self.hash(attachment_data))

        return self.cached_attachment_hashes

    # returns True if two message fingerprints are similar
    # specifically, if at least one of the attachments are identical
    # or if the message body is identical and not blank
    async def matches(self, other: "MessageFingerprint") -> bool:
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
    async def is_multipost_of(self, other: "MessageFingerprint") -> bool:
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
        self.fingerprints: list[
            MessageFingerprint
        ] = (
            []
        )  # stores all user messages sent in the last minute (recent messages near the end)
        self.multipost_warnings: dict[
            Annotated[int, "Multiposted Message ID"],
            tuple[
                Annotated[discord.Message, "Bot's Warning Message"],
                Annotated[MessageFingerprint, "Offending Message's Fingerprint"],
            ],
        ] = {}
        self.clear_old_cached_data.start()

    # Records and returns a MessageFingerprint and a list of fingerprints that this message is a multipost of
    async def record_fingerprint(
        self,
        message: discord.Message,
    ) -> tuple[MessageFingerprint, list[MessageFingerprint]]:
        fingerprint = MessageFingerprint.build(message)
        self.fingerprints.append(fingerprint)

        multipost_of: list[MessageFingerprint] = []
        for other_fingerprint in self.fingerprints:
            if (
                fingerprint is not other_fingerprint
                and await fingerprint.is_multipost_of(other_fingerprint)
            ):
                multipost_of.append(other_fingerprint)

        return fingerprint, multipost_of

    # deletes recorded fingerprints after 2 minutes,
    # and clears out logged `multipost_warnings` after 10 minutes
    @tasks.loop(seconds=3)
    async def clear_old_cached_data(self) -> None:
        # new messages are always appended to the end of the list
        # so we will only be deleting messages from the front of the list
        # this algorithm finds the number of messages the delete, then deletes them in bulk
        n_fingerprints_to_delete = 0
        for fingerprint in self.fingerprints:
            if time.time() - fingerprint.created_at > 120:
                n_fingerprints_to_delete += 1
            else:
                break

        del self.fingerprints[:n_fingerprints_to_delete]

        # delete multipost warnings that are more than 10 minutes old
        multipost_warnings_to_delete = [
            original_message_id
            for original_message_id, (
                warning_message,
                _fingerprint,
            ) in self.multipost_warnings.items()
            if time.time() - warning_message.created_at.timestamp() > 600
        ]
        for message_id in multipost_warnings_to_delete:
            del self.multipost_warnings[message_id]

    async def delete_previous_multipost_warnings(
        self,
        channel_id: int,
        author_id: int,
    ) -> None:
        to_delete = [
            warning_message_id
            for warning_message_id, (
                multipost_warning,
                offenders_fingerprint,
            ) in self.multipost_warnings.items()
            if offenders_fingerprint.channel_id == channel_id
            and offenders_fingerprint.author_id == author_id
        ]
        for warning_message_id in to_delete:
            multipost_warning, _offenders_fingerprint = self.multipost_warnings.pop(
                warning_message_id,
            )
            await multipost_warning.delete()

    # this function should be called after every on_message
    # it will detect multiposts and will apply the following moderation:
    #   - Original Message - No action taken
    #   - Second Message - React to both the original and second message with a custom emoji, and warn the author under the second message
    #   - Third and Subsequent Messages - Delete the message and warn the author, then delete the warning after 15 seconds
    # A message is a "multipost" if it meets these criteria:
    #   - Author is not a bot
    #   - Author doesn't have the ALLOW_MULTIPOST_FOR_ROLE role
    #   - Message was sent in a TextChannel (not a DMChannel) that is in a CategoryChannel whose name ends with "HELP"
    #   - The same author sent another message in the last 60 seconds with a matching fingerprint (see MessageFingerprint.matches)
    async def check_multipost(self, message: discord.Message) -> None:
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

        fingerprint, previous_messages = await self.record_fingerprint(message)
        n_previous_messages = len(previous_messages)

        # Original Message - No action taken
        if n_previous_messages == 0:
            return

        # First Multipost - React to the original message with a custom multipost emoji, and reply with a warning to the multipost
        if n_previous_messages == 1:
            original_message = previous_messages[0]

            embed = EmbedBuilder(
                title="Multi-Post Warning",
                description="Please don't send the same message in multiple channels.",
                fields=[
                    (
                        "Original Message",
                        f"[link]({original_message.jump_url})",
                        True,
                    ),
                ],
            ).build()

            try:
                await self.bot.http.add_reaction(
                    original_message.channel_id,
                    original_message.message_id,
                    MULTIPOST_EMOJI,
                )
                await message.add_reaction(MULTIPOST_EMOJI)

                warning = await message.reply(embed=embed)
                await self.delete_previous_multipost_warnings(
                    fingerprint.channel_id,
                    fingerprint.author_id,
                )
                self.multipost_warnings[message.id] = (warning, fingerprint)
                log(f"First mp warning for $ in {message.channel.name}", message.author)
            except discord.errors.HTTPException as e:
                if "unknown message".casefold() in repr(e).casefold():
                    # The multipost has already been deleted, take no action
                    return
                # unknown error, just raise it
                raise

        # Subsequent Multiposts - Reply with a warning (and ping the offender), delete the multipost, then delete the warning after 15 seconds
        else:
            first_message, second_message, *_other_messages = previous_messages

            embed = EmbedBuilder(
                title="Multi-Post Deleted",
                description="Please don't send the same message in multiple channels. Your message has been deleted.",
                fields=[
                    (
                        "First Message",
                        f"[link]({first_message.jump_url})",
                        True,
                    ),
                    (
                        "Second Message",
                        f"[link]({second_message.jump_url})",
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
                    f"Subsequent mp warning for $ in {message.channel.name}",
                    message.author,
                )
            except discord.errors.HTTPException as e:
                if "unknown message".casefold() in repr(e).casefold():
                    # The multiposted message has already been deleted, take no action
                    return
                # unknown error, just raise it
                raise

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message) -> None:
        await self.check_multipost(message)

    @commands.Cog.listener()
    async def on_raw_message_delete(
        self,
        payload: discord.RawMessageDeleteEvent,
    ) -> None:
        if payload.message_id in self.multipost_warnings:
            # The person deleted their message after seeing out multipost warning
            # so we can delete the warning message
            warning_message, _fingerprint = self.multipost_warnings.pop(
                payload.message_id,
            )
            try:
                await warning_message.delete()
            except discord.errors.HTTPException as e:
                if "unknown message".casefold() in repr(e).casefold():
                    # a mod probably already deleted the warning message
                    return
                raise

        # If you delete your message then re-send it in another channel, that's fine
        # so we can remove the original message fingerprint
        for i, fingerprint in enumerate(self.fingerprints):
            if payload.message_id == fingerprint.message_id:
                del self.fingerprints[i]
                break


def setup(bot: commands.Bot) -> None:
    bot.add_cog(Moderation(bot))
