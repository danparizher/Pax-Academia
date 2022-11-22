import string
import time
from dataclasses import dataclass
from hashlib import sha256
from typing import TypeAlias

import aiohttp
import discord
from discord.ext import commands, tasks

import util.bandwidth as bandwidth
from util.EmbedBuilder import EmbedBuilder
from util.Logging import log

# hashlib just returns a bytes object, so this allows for slightly stricter typing
Hash: TypeAlias = bytes


@dataclass
class MessageFingerprint:
    created_at: float  # unix timestamp
    author_id: int
    guild_id: int | None  # will be None for DMs
    channel_id: int
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
    def build(cls, message: discord.Message) -> "MessageFingerprint":
        filtered_content = cls.filter_content(message.content)

        return cls(
            created_at=time.time(),
            author_id=message.author.id,
            guild_id=message.guild.id if message.guild else None,
            channel_id=message.channel.id,
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
                }
            )
        )

        if len(content) < 15:
            return None

        return content

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
                        async with session.get(attachment_url) as resp:
                            attachment_data = await resp.read()
                            bandwidth.log(
                                len(
                                    attachment_data
                                ),  # this doesn't account for HTTP/TCP overhead or compression
                                "inbound",
                                "download_attachment",
                                f"HTTP GET {attachment_url}",
                            )
                    except Exception as e:
                        # it's possible that Discord may have deleted the attachment, and so we would get a 404
                        # furthermore, it's not super important that this function is 100% perfectly accurate
                        # so it's fine to just log and ignore any errors
                        log(
                            f"Error occurred while downloading attachment for message fingerprinting. Attachment URL: `{attachment_url}`, Error: {e}"
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
        self.delete_old_fingerprints_task.start()

    # temporarily commented out because this is not functional
    """
    @commands.slash_command(name="mkick", description="Kicks multiple users from the server.")
    @commands.has_permissions(kick_members=True)
    async def mkick(
        self,
        ctx: commands.Context,
        users: option(
            name="users",
            description="The users to kick.",
            type=str,
            required=True,
        ),
        reason: option(
            name="reason",
            description="The reason for kicking the user.",
            type=str,
            required=False,
        ),
    ) -> None:
        for user_id in users.split(" "):
            user = ctx.guild.get_member(int(user_id))
            if user is not None:
                await ctx.guild.kick(user, reason=reason)
        embed = EmbedBuilder(
            title="Success!",
            description=f"Successfully kicked {len(users)} users.",
        ).build()
        await ctx.respond(embed=embed)
    """

    # Records a MessageFingerprint and returns a fingerprint that this message is a multipost of, if there is one.
    async def record_fingerprint(
        self, message: discord.Message
    ) -> MessageFingerprint | None:
        fingerprint = MessageFingerprint.build(message)

        # find existing multipost
        multipost_of = None
        for other_fingerprint in self.fingerprints:
            if await fingerprint.is_multipost_of(other_fingerprint):
                multipost_of = other_fingerprint
                break

        # this has to happen _after_ the `matching_fingerprint` loop because a fingerprint always matches itself
        self.fingerprints.append(fingerprint)

        return multipost_of

    # deletes recorded fingerprints after 60 seconds
    @tasks.loop(seconds=3)
    async def delete_old_fingerprints_task(self):
        # new messages are always appended to the end of the list
        # so we will only be deleting messages from the front of the list
        # this algorithm finds the number of messages the delete, then deletes them in bulk
        n_fingerprints_to_delete = 0
        for fingerprint in self.fingerprints:
            if time.time() - fingerprint.created_at > 60:
                n_fingerprints_to_delete += 1
            else:
                break

        del self.fingerprints[:n_fingerprints_to_delete]

    # this function should be called after every on_message
    # it will detect multiposts and reply with a warning
    # A message is a "multipost" if it meets these criteria:
    #   - Author is not a bot
    #   - Message was sent in a TextChannel (not a DMChannel) that is in a CategoryChannel whose name ends with "HELP"
    #   - The same author sent another message in the last 60 seconds with a matching fingerprint (see MessageFingerprint.matches)
    async def check_multipost(self, message: discord.Message) -> None:
        # author not a bot
        if message.author.bot:
            return

        # textchannel in category ending with "HELP"
        if not isinstance(message.channel, discord.TextChannel):
            return
        if (
            not message.channel.category
            or not message.channel.category.name.lower().endswith("help")
        ):
            return

        # matching fingerprint
        matching_previous_message = await self.record_fingerprint(message)
        if not matching_previous_message:
            return

        # all criteria met - a multipost has been detected!
        # reply with a warning embed
        if matching_previous_message.channel_id == message.channel.id:
            description = "Please don't send the same message multiple times."
        else:
            description = "Please don't send the same message in multiple channels."
        embed = EmbedBuilder(
            title="Multi-Post Warning",
            description=description,
            fields=[
                (
                    "Original Message",
                    f"[link]({matching_previous_message.jump_url})",
                    True,
                )
            ],
        ).build()

        await message.reply(embed=embed)

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message) -> None:
        await self.check_multipost(message)


def setup(bot: commands.Bot) -> None:
    bot.add_cog(Moderation(bot))
