import discord
from discord.ext import commands

from util.EmbedBuilder import EmbedBuilder


class Misc(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @commands.slash_command(name="ping", description="Pings the bot.")
    async def ping(self, ctx: commands.Context) -> None:
        """
        It creates an embed with the title "Pong!" and the description "Latency: {round(self.bot.latency *
        1000)}ms" and then sends it to the channel the command was used in
        
        :param ctx: commands.Context
        :type ctx: commands.Context
        """
        embed = EmbedBuilder(
            title="Pong!",
            description=f"Latency: {round(self.bot.latency * 1000)}ms",
        ).build()

        await ctx.respond(embed=embed)

    @commands.Cog.listener()
    async def on_ready(self) -> None:
        """
        The above function is a coroutine that prints a message to the console when the bot is ready
        """
        print(f"{self.bot.user.name} has connected to Discord!")
        await self.bot.change_presence(
            activity=discord.Activity(
                name="Academic Peace...", type=discord.ActivityType.watching
            )
        )


def setup(bot: commands.Bot) -> None:
    bot.add_cog(Misc(bot))
