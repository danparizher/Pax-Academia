import aiohttp
import bs4
from discord import option
from discord.ext import commands

from util.EmbedBuilder import EmbedBuilder
from util.Logging import log


async def request(word: str) -> bs4.BeautifulSoup:
    """
    It takes a word as a string, and returns a BeautifulSoup object of the word's Merriam-Webster page

    :param word: str
    :type word: str
    :return: A BeautifulSoup object.
    """
    url = f"https://www.merriam-webster.com/dictionary/{word}"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            soup = bs4.BeautifulSoup(await response.text(), "html.parser")
    return soup


async def spellcheck(word: str) -> str:
    """
    It takes a word as an argument, makes a request to the website, parses the response, and returns the
    spelling suggestions

    :param word: str - The word to be checked
    :type word: str
    :return: The return value is a string.
    """
    try:
        soup = await request(word.lower())
        spelling = soup.find("p", {"class": "spelling-suggestions"}).text
        return spelling.strip().capitalize()
    except (AttributeError, IndexError):
        return "No spelling suggestions found"


async def get_word_info(word: str) -> dict:
    """
    It takes a word as an argument, and returns a dictionary containing the word's definition, phonetic,
    synonyms, antonyms, usage, and etymology.

    :param word: str - The word you want to get the information of
    :type word: str
    :return: A dictionary with the word, definition, phonetic, synonyms, antonyms, usage, and etymology.
    """
    word_data = {}
    soup = await request(word.lower())
    word_data["word"] = word
    try:
        word_data["definition"] = soup.find("span", {"class": "dtText"}).text.split(
            ":"
        )[1]
    except (AttributeError, IndexError):
        word_data["definition"] = "No definition found"
    try:
        word_data["phonetic"] = soup.find("span", {"class": "pr"}).text.replace(" ", "")
    except (AttributeError, IndexError):
        word_data["phonetic"] = "No phonetic found"
    try:
        word_data["synonyms"] = soup.find("ul", {"class": "mw-list"}).find_all("li")
        word_data["synonyms"] = ", ".join(
            [
                synonym.text.replace(", ", "").capitalize()
                for synonym in word_data["synonyms"]
                if "(" not in synonym.text
            ]
        )
    except (AttributeError, IndexError):
        word_data["synonyms"] = "No synonyms found"
    try:
        word_data["antonyms"] = soup.find_all("ul", {"class": "mw-list"})[1].find_all(
            "li"
        )
        word_data["antonyms"] = ", ".join(
            [
                antonym.text.replace(", ", "").capitalize()
                for antonym in word_data["antonyms"]
                if "(" not in antonym.text
            ]
        )
    except (AttributeError, IndexError):
        word_data["antonyms"] = "No antonyms found"
    try:
        word_data["usage"] = soup.find("p", {"class": "ety-sl"}).text
        word_data["usage"] = word_data["usage"].split(",")[0]
    except (AttributeError, IndexError):
        word_data["usage"] = "No use found"
    try:
        word_data["etymology"] = soup.find_all("p", {"class": "et"})[0].text.split("—")[
            0
        ]
    except (AttributeError, IndexError):
        word_data["etymology"] = "No etymology found"
    return word_data


class Dictionary(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @commands.slash_command(name="define", description="Defines a word.")
    @option("word", str, description="The word to define.", required=True)
    async def define(self, ctx: commands.Context, word: str) -> None:
        """
        It takes a word as an argument, and returns the definition of that word

        :param ctx: commands.Context
        :type ctx: commands.Context
        :param word: str
        :type word: str
        :return: The word_data variable is being returned.
        """
        await ctx.defer()
        if " " in word:
            embed = EmbedBuilder(
                title="Error",
                description="Please enter a single word.",
            ).build()
            await ctx.respond(embed=embed)
            return
        try:
            word_data = await get_word_info(word)
            old_word = ""
            if word_data["definition"] == "No definition found":
                old_word = word
                word_data = await get_word_info(await spellcheck(word))
                if word_data["definition"] == "No definition found":
                    await ctx.edit(
                        content=f"No results found for **{old_word.capitalize()}**."
                    )
                    return

            embed = EmbedBuilder(
                title=f"Definition of __{word_data['word'].capitalize()}__",
                description=word_data["definition"],
                fields=[
                    ("Phonetic Pronunciation", word_data["phonetic"], False),
                    ("Synonyms", word_data["synonyms"], True),
                    ("Antonyms", word_data["antonyms"], True),
                    ("First Known Use", word_data["usage"], False),
                    ("Etymology", word_data["etymology"], False),
                ],
            ).build()

            content = (
                None
                if old_word == ""
                else f"No results found for **{old_word.capitalize()}**. Did you mean **{word_data['word'].capitalize()}**?"
            )
            await ctx.edit(content=content, embed=embed)

            log(f"Define command used by {ctx.author} in {ctx.guild}.")

        except Exception as e:
            embed = EmbedBuilder(
                title=f"Definition of __{word.capitalize()}__",
                description=f"An error occurred while trying to define {word.capitalize()}:\n\n{e}",
            ).build()
            await ctx.edit(embed=embed)


def setup(bot) -> None:
    bot.add_cog(Dictionary(bot))
