from dataclasses import dataclass
from typing import TypeAlias, Optional
from hashlib import sha256
import urllib.request
import aiohttp

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
    content_hash: Hash  # the hash

    attachment_urls: list[str]  # the discord content URLs for each of the message's uploaded attachments
    _cached_attachment_hashes: Optional[set[Hash]] = None  # populated on the first call to `get_attachment_hashes`

    # performs a SHA256 hash
    @staticmethod
    def hash(data: str | bytes) -> Hash:
        if isinstance(data, str):
            data = data.encode()

        return sha256(data).digest()

    async def get_attachment_hashes(self) -> set[Hash]:
        if self._cached_attachment_hashes is None:
            self._cached_attachment_hashes = set()

            async with aiohttp.ClientSession() as session:
                for attachment_url in self.attachment_urls:
                    try:
                        async with session.get(attachment_url) as resp:
                            attachment_data = await resp.read()
                    except:
                        # it's possible that Discord may have deleted the attachment, and so we would get a 404
                        # furthermore, it's not super important that this function is 100% perfectly accurate
                        # so it's fine to just silently drop any errors
                        continue

                    self._cached_attachment_hashes.add(self.hash(attachment_data))

        return self._cached_attachment_hashes


# TODO: Incomplete/in testing. Do not add to cog list.
class Moderation(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

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


def setup(bot: commands.Bot) -> None:
    bot.add_cog(Moderation(bot))
