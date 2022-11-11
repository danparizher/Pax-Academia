import discord
from discord import option
from discord.ext import commands

from util.EmbedBuilder import EmbedBuilder


class Information(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @commands.slash_command(
        name="attempt", description="Asks the user what they have attempted so far."
    )
    @option(
        name="user",
        description="The user to ping.",
        type=discord.User,
        required=False,
    )
    async def attempt(self, ctx: commands.Context, user: discord.User) -> None:
        embed = EmbedBuilder(
            title="What have you attempted so far?",
            description="Please show and describe the steps you have completed so that we may help you further.",
        ).build()
        await ctx.respond(content=f"<@{user.id}>" if user else None, embed=embed)

    @commands.slash_command(
        name="codehelp", description="Shows the user how to format their code question."
    )
    @option(
        name="user",
        description="The user to ping.",
        type=discord.User,
        required=False,
    )
    async def codehelp(self, ctx: commands.Context, user: discord.User) -> None:
        embed = EmbedBuilder(
            title="Code Formatting",
            description="Please format your code using the following syntax:\n\`\`\`python\n# Your code here\n\`\`\`\n\nThe code will be formatted as follows:\n```python\n# Your code here\n```\n\nIf you are using a language other than Python, replace `python` with the name of your language.\n\n- Please explain what is not working, and what you have attempted so far.\n- Always show your entire code, not just the part that is not working.\n- If you are getting an error, please show the entire error message.",
        ).build()
        await ctx.respond(content=f"<@{user.id}>" if user else None, embed=embed)


def setup(bot: commands.Bot) -> None:
    bot.add_cog(Information(bot))
