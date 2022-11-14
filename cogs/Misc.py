import discord
from discord.ext import commands


class Misc(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @commands.slash_command(name="ping", description="Pings the bot.")
    async def ping(self, ctx: commands.Context) -> None:
        """
        It sends a message, then edits that message to say "Pong!" and the latency of the bot
        
        :param ctx: The context of the command
        :type ctx: commands.Context
        """
        message = await ctx.respond("Pinging...")
        await message.edit_original_response(
            content=f"Pong! {round(self.bot.latency * 1000)}ms"
        )

    @commands.Cog.listener()
    async def on_ready(self) -> None:
        """
        The above function is a coroutine that prints a message to the console when the bot is ready
        """
        print(f"{self.bot.user.name} has connected to Discord!")
        await self.bot.change_presence(activity=discord.Game(name="Academic Peace..."))


def setup(bot: commands.Bot) -> None:
    bot.add_cog(Misc(bot))
