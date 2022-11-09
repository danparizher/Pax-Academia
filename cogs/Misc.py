import time

import discord
from discord.ext import commands


class Misc(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @commands.slash_command()
    async def ping(self, ctx: commands.Context) -> None:
        start = time.time()
        message = await ctx.respond("Pong!")
        end = time.time()
        await message.edit_original_response(
            content=f"Pong! `{round((end - start) * 1000)}ms`"
        )

    @commands.Cog.listener()
    async def on_ready(self) -> None:
        print(f"{self.bot.user.name} has connected to Discord!")
        await self.bot.change_presence(activity=discord.Game(name="Academic Peace..."))


def setup(bot: commands.Bot) -> None:
    bot.add_cog(Misc(bot))
