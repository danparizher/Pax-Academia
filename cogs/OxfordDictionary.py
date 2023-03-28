import contextlib

import aiohttp
import bs4
from discord import option
from discord.ext import commands

from util.EmbedBuilder import EmbedBuilder
from util.Logging import Log


async def request(word: str) -> bs4.BeautifulSoup:
    """
    It takes a word as a string, and returns a BeautifulSoup object of the word's Merriam-Webster page
    :param word: str
    :type word: str
    :return: A BeautifulSoup object.
    """

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36",
    }
    async with aiohttp.ClientSession(headers=headers) as session:
        async with session.get(
            f"https://www.oxfordlearnersdictionaries.com/definition/english/{word}",
        ) as response:
            return bs4.BeautifulSoup(await response.text(), "html.parser")


async def spellcheck(word: str) -> str:
    """
    It takes a word, makes a request to the website, and returns the first suggested spelling

    :param word: str - The word to be spellchecked
    :type word: str
    :return: The spelling of the word.
    """
    with contextlib.suppress(AttributeError, IndexError):
        soup = await request(word.lower())
        spelling = soup.find("a", {"class": "dym-link"}).text
        return spelling.strip().capitalize()


async def get_word_info(word: str) -> dict:
    """
    It takes a word as input, and returns a dictionary containing the word's definition, grammar,
    examples, pronunciation, part of speech, and synonyms

    :param word: str - The word you want to look up
    :type word: str
    :return: A dictionary with the word and its information.
    """
    soup = await request(word.lower())
    word_data = {"word": word}
    try:
        word_data["Definition"] = soup.find("span", {"class": "def"}).text.strip()
        if word_data["Definition"][-1] != ".":
            word_data["Definition"] += "."
    except (AttributeError, IndexError):
        word_data["Definition"] = "No definition found"

    try:
        word_data["Grammar"] = soup.find("span", {"class": "grammar"}).text.strip()
        word_data["Grammar"] = word_data["Grammar"].replace("[", "").replace("]", "")
        word_data["Grammar"] = word_data["Grammar"].capitalize()
    except (AttributeError, IndexError):
        word_data["Grammar"] = "No grammar found"

    try:
        word_data["Example"] = (
            soup.find("span", {"class": "x"}).text.strip().capitalize()
        )
    except (AttributeError, IndexError):
        word_data["Example"] = "No examples found"

    try:
        word_data["Phonetic Pronunciation"] = soup.find("span", {"class": "phon"}).text
    except (AttributeError, IndexError):
        word_data["Phonetic Pronunciation"] = "No pronunciation found"

    try:
        word_data["Part of speech"] = soup.find(
            "span",
            {"class": "pos"},
        ).text.capitalize()
    except (AttributeError, IndexError):
        word_data["Part of speech"] = "No PoS found"

    try:
        word_data["Synonyms"] = soup.find("span", {"class": "xh"}).text.capitalize()
    except (AttributeError, IndexError):
        word_data["Synonyms"] = "No synonyms found"

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
            if word_data["Definition"] == "No definition found":
                old_word = word
                word_data = await get_word_info(await spellcheck(word))
            if word_data["Definition"] == "No definition found":
                await ctx.edit(
                    content=f"No results found for **{old_word.capitalize()}**. Did you spell it correctly?",
                )
                return

            fields = [
                [key.title(), value, False]
                for key, value in word_data.items()
                if (
                    value != f"No {key.lower()} found"
                    and key != "word"
                    and key != "Definition"
                )
            ]
            embed = EmbedBuilder(
                title=f"Definition of __{word_data['word'].capitalize()}__",
                description=word_data["Definition"].capitalize(),
                fields=fields or None,
            ).build()

            content = (
                f"No results found for **{old_word.capitalize()}**. Did you mean **{word_data['word'].capitalize()}**?"
                if old_word
                else None
            )
            await ctx.edit(content=content, embed=embed)

            Log(f"Define command used by {ctx.author} in {ctx.guild}.")

        except Exception as e:
            embed = EmbedBuilder(
                title=f"Definition of __{word.capitalize()}__",
                description=f"An error occurred while trying to define {word.capitalize()}:\n\n{e}",
            ).build()
            await ctx.edit(embed=embed)


def setup(bot: commands.Bot) -> None:
    bot.add_cog(Dictionary(bot))
