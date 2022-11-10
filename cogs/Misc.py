import discord
from discord.ext import commands


class Misc(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @commands.slash_command(name="ping", description="Pings the bot.")
    async def ping(self, ctx: commands.Context) -> None:
        message = await ctx.respond("Pinging...")
        await message.edit_original_response(
            content=f"Pong! {round(self.bot.latency * 1000)}ms"
        )

    @commands.Cog.listener()
    async def on_ready(self) -> None:
        print(f"{self.bot.user.name} has connected to Discord!")
        await self.bot.change_presence(activity=discord.Game(name="Academic Peace..."))


def setup(bot: commands.Bot) -> None:
    bot.add_cog(Misc(bot))
