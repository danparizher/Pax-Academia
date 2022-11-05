import discord
from discord.ext import commands


class Misc(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @commands.command()
    async def ping(self, ctx: commands.Context) -> None:
        await ctx.send("Pong!")

    @commands.Cog.listener()
    async def on_ready(self) -> None:
        print(f"{self.bot.user.name} has connected to Discord!")
        await self.bot.change_presence(activity=discord.Game(name="Academic Peace..."))


def setup(bot: commands.Bot) -> None:
    bot.add_cog(Misc(bot))
