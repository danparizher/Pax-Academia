from dataclasses import dataclass
from typing import TypeAlias, Optional
from hashlib import sha256
import urllib.request
import aiohttp
import re

import discord
from discord.commands import option
from discord.ext import commands, tasks

from util.EmbedBuilder import EmbedBuilder

# hashlib just returns a bytes object
Hash: TypeAlias = bytes

# this is a simple structure that stores important information
@dataclass
class MessageFingerprint:
    author_id: discord.Snowflake
    channel_id: discord.Snowflake

    attachment_urls: list[str]  # the discord content URLs for each of the message's uploaded attachments
    cached_attachment_hashes: Optional[set[Hash]] = None  # populated on the first call to `get_attachment_hashes`

    content_hash: Optional[
        Hash
    ] = None  # hash of the message body (with whitespace removed), or None if there is no message body

    # shortcut to build a fingerprint given a message
    @classmethod
    def build(cls, message: discord.Message) -> "MessageFingerprint":

        content_without_whitespace = re.sub(r"\s", "", message.content)
        return cls(
            author_id=message.author.id,
            channel_id=message.channel.id,
            attachment_urls=[attachment.url for attachment in message.attachments],
            content_hash=cls.hash(content_without_whitespace) if content_without_whitespace else None,
        )

    # performs a SHA256 hash
    @staticmethod
    def hash(data: str | bytes) -> Hash:
        if isinstance(data, str):
            data = data.encode()

        return sha256(data).digest()

    # retrieves and caches attachment hashes
    # the first call will actually download every attachment,
    # and all subsequent calls will just return the cached values
    async def get_attachment_hashes(self) -> set[Hash]:
        if self.cached_attachment_hashes is None:
            self.cached_attachment_hashes = set()

            async with aiohttp.ClientSession() as session:
                for attachment_url in self.attachment_urls[:5]:  # only load first 5 attachments to prevent abuse
                    try:
                        async with session.get(attachment_url) as resp:
                            attachment_data = await resp.read()
                    except:
                        # it's possible that Discord may have deleted the attachment, and so we would get a 404
                        # furthermore, it's not super important that this function is 100% perfectly accurate
                        # so it's fine to just silently drop any errors
                        continue

                    self.cached_attachment_hashes.add(self.hash(attachment_data))

        return self.cached_attachment_hashes

    # returns True if two message fingerprints are similar (i.e. if the message is a 'multipost')
    # specifically, if at least one of the attachments are identical or if the message body
    # is identical and not blank
    async def matches(self, other: "MessageFingerprint") -> bool:
        # different authors cannot have matching fingerprints
        if self.author_id != other.author_id:
            return False

        # if there is content and it matches, then the fingerprint matches
        if self.content_hash is not None and (self.content_hash == other.content_hash):
            return True

        # otherwise, at least one of the attachments must match
        matching_attachments = await self.get_attachment_hashes() & await other.get_attachment_hashes()
        return len(matching_attachments) > 0


class Moderation(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

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


def setup(bot: commands.Bot) -> None:
    bot.add_cog(Moderation(bot))
