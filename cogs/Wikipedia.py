import asyncio

import wikipedia
from discord.ext import commands

from util.embedbuilder import EmbedBuilder
from util.Logging import Log, limit


def get_wiki_without_logging(query: str) -> dict[str, str]:
    """
    It takes a query, gets the first page from Wikipedia, and returns a dictionary with the title,
    summary, url, and image of the page

    :param query: The query to search for
    :return: A dictionary with the title, summary, url, and image of the wikipedia page.
    """
    page = wikipedia.page(query, auto_suggest=False)
    return {
        "title": page.title,
        "summary": page.summary.split("\n")[0],
        "url": page.url,
        "image": page.images[0],
    }


async def get_wiki(query: str) -> dict[str, str]:
    return await asyncio.to_thread(get_wiki_without_logging, query)


class Wikipedia(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @commands.slash_command(name="wiki", description="Searches Wikipedia for a topic.")
    @limit(2)
    async def wiki(self, ctx: commands.Context, query: str) -> None:
        """
        It searches Wikipedia for a query and returns the first result

        :param ctx: commands.Context
        :type ctx: commands.Context
        :param query: str
        :type query: str
        """
        try:
            page = await get_wiki(query)
            embed = EmbedBuilder(
                title=page["title"].title(),
                description=page["summary"],
                url=page["url"],
                image=page["image"],
            ).build()

            await ctx.respond(embed=embed)

            Log(f"Wikipedia command used by $ in {ctx.guild}.", ctx.author)

        except wikipedia.exceptions.DisambiguationError:
            embed = EmbedBuilder(
                title="Error",
                description="The search term you entered is ambiguous. Please be more specific.",
            ).build()

            await ctx.respond(embed=embed, ephemeral=True)

        except wikipedia.exceptions.PageError:
            embed = EmbedBuilder(
                title="Error",
                description="The search term you entered does not exist on Wikipedia.",
            ).build()

            await ctx.respond(embed=embed, ephemeral=True)


def setup(bot: commands.Bot) -> None:
    bot.add_cog(Wikipedia(bot))
