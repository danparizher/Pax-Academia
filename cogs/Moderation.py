import discord
from discord.commands import option
from discord.ext import commands

from util.EmbedBuilder import EmbedBuilder


# TODO: Incomplete/in testing. Do not add to cog list.
class Moderation(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @commands.slash_command(
        name="mkick", description="Kicks multiple users from the server."
    )
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
