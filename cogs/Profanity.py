import discord
from discord.ext import commands
from profanity_check import predict_prob

from util.EmbedBuilder import EmbedBuilder


class Profanity(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message) -> None:
        if message.author.bot:
            return

        if predict_prob([message.content])[0] > 0.8:
            embed = EmbedBuilder(
                title="Profanity Detected",
                description=f"This message has a value of {predict_prob([message.content])[0] * 100:.2f}%.",
            )
            await message.channel.send(embed=embed.build())


def setup(bot: commands.Bot) -> None:
    bot.add_cog(Profanity(bot))
