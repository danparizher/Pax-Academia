import asyncio
import re
import urllib.parse
from dataclasses import dataclass

import aiohttp
import bs4
import discord
from discord import option
from discord.commands.context import ApplicationContext
from discord.ext import commands

from util.EmbedBuilder import EmbedBuilder
from util.Logging import Log, limit


@dataclass
class Pronunciation:
    phonetic: str
    audio_url: str | None = None

    def __str__(self) -> str:
        """
        Formats a hyperlink for Discord markdown.

        :return: a string like "[/ɡreɪt/](https://www.oxfordlearnersdictionaries.com/media/english/uk_pron_ogg/g/gre/great/great__gb_1.ogg)"
        """
        if self.audio_url:
            return f"[{self.phonetic}]({self.audio_url})"

        return self.phonetic

    @classmethod
    def parse_from_oxford_phonetic_element(
        cls: type["Pronunciation"],
        element: bs4.Tag,
    ) -> "Pronunciation | None":
        """
        Tries to parse a pronunciation element on an Oxford dictionary page.

        :param element: The element from the Oxford dictionary page.
                        Should be a <div> under the <span class="phonetics"> element.
        :return: a Pronunciation if successful, and None otherwise
        """

        if phonetic_element := element.select_one(".phon"):
            pronunciation = cls(phonetic=phonetic_element.text.strip())
            if not pronunciation.phonetic:
                return None

            if audio_element := element.select_one(".sound"):
                if audio_element.has_attr("data-src-mp3"):
                    pronunciation.audio_url = str(audio_element["data-src-mp3"])
                elif audio_element.has_attr("data-src-ogg"):
                    pronunciation.audio_url = str(audio_element["data-src-ogg"])

            return pronunciation

        return None


@dataclass
class Example:
    sentence: str
    labels: str | None  # i.e. "(informal) (ironic)"

    def __str__(self) -> str:
        """
        Formats the example for Discord markdown.

        :return: a string like "*(ironic)* Oh great, they left without us."
        """

        return f"*{self.labels}* {self.sentence}" if self.labels else self.sentence


@dataclass
class Sense:
    definition: str
    grammar: str | None  # i.e. "[usually before noun]"
    labels: str | None  # i.e. "(informal) (ironic)"
    examples: list[Example]

    def __str__(self) -> str:
        """
        Formats the sense for Discord markdown without any examples.

        :return: a string like "*[only before noun] (informal)* used to emphasize an adjective of size or quality"
        """
        if self.grammar:
            if self.labels:
                return f"*{self.grammar} {self.labels}* {self.definition}"
            return f"*{self.grammar}* {self.definition}"
        return f"*{self.labels}* {self.definition}" if self.labels else self.definition


@dataclass
class SimilarWord:
    word: str
    url: str
    part_of_speech: str | None

    async def fetch(self) -> "WordInformation":
        """
        Fetches the word information based on the URL.

        :return: a WordInformation
        """
        status_code, soup = await fetch_page_cached(self.url)
        assert (
            status_code == 200
        ), "Got a non-200 response while fetching a URL that was provided directly from Oxford."
        return parse_oxford_definition_page(self.url, soup)


@dataclass
class WordInformation:
    US_FLAG_EMOJI = (
        "\N{REGIONAL INDICATOR SYMBOL LETTER U}\N{REGIONAL INDICATOR SYMBOL LETTER S}"
    )
    GB_FLAG_EMOJI = (
        "\N{REGIONAL INDICATOR SYMBOL LETTER G}\N{REGIONAL INDICATOR SYMBOL LETTER B}"
    )
    SPEAKING_HEAD_EMOJI = "\N{SPEAKING HEAD IN SILHOUETTE}\N{VARIATION SELECTOR-16}"

    url: str
    word: str
    part_of_speech: str | None
    us_pronunciation: Pronunciation | None
    gb_pronunciation: Pronunciation | None
    senses: list[Sense]
    similar_words: list[
        SimilarWord
    ]  # may include words with identical spellings, but differing parts of speech

    def build_embed(self) -> discord.Embed:
        """
        Builds an embed that contains all the relevant information.
        Will only include the first 5 definitions with max 3 examples each, or 5 examples if there is only one definition.

        :return: a discord.Embed
        """
        title = f"*{self.word.title()}*"
        footer = "Retrieved from Oxford Learner's Dictionary by Homework Help"

        header = ""

        if self.part_of_speech:
            header += f"**{self.part_of_speech}**\n"

        if self.us_pronunciation and self.gb_pronunciation:
            header += f"{WordInformation.US_FLAG_EMOJI} **{self.us_pronunciation}**\n"
            header += f"{WordInformation.GB_FLAG_EMOJI} **{self.gb_pronunciation}**\n"
        elif self.us_pronunciation or self.gb_pronunciation:
            header += f"{WordInformation.SPEAKING_HEAD_EMOJI} **{self.us_pronunciation or self.gb_pronunciation}**\n"

        header = header.strip()

        if len(self.senses) == 1:
            sense = self.senses[0]
            description = f"{header}\n\n{sense}".strip()

            if sense.examples:
                fields = [
                    (
                        "Examples",
                        "\n".join(
                            f"**\N{BULLET}** {example}"
                            for example in sense.examples[:5]
                        ),
                        True,
                    ),
                ]
            else:
                fields = None

            return EmbedBuilder(
                title=title,
                description=description,
                fields=fields,
                footer=footer,
            ).build()

        assert (
            len(self.senses) > 1
        ), "It shouldn't be possible for a WordInformation to be created without a sense."

        sense_parts = []
        for index, sense in enumerate(self.senses[:5]):
            part = f"**{index + 1}.** {sense}"
            if sense.examples:
                part += "\n"
                part += "\n".join(
                    f"\N{ZERO WIDTH SPACE}    **\N{BULLET}** {example}"
                    for example in sense.examples[:3]
                )
            sense_parts.append(part)
        senses = "\n\n".join(sense_parts)

        description = f"{header}\n\n{senses}".strip()

        return EmbedBuilder(
            title=title,
            description=description,
            footer=footer,
        ).build()


# a FILO stack of (URL, Page) elements
# - new entries are at the beginning
# - after a cache hit, the page is moved back to the beginning
page_cache: list[tuple[str, bs4.BeautifulSoup]] = []
PAGE_CACHE_SIZE = 16


async def fetch_page_cached(url: str) -> tuple[int, bs4.BeautifulSoup]:
    """
    Simple utility function to HTTP GET the page.
    Caches the most recent 16 URLs (only for 200 status codes).

    :param url: the URL to fetch
    :return: the status code and the BeautifulSoup-parsed page
    """

    # check if already cached
    for index, (cached_url, cached_page) in enumerate(page_cache):
        if cached_url == url:
            # move to the front of the array, so it won't be deleted soon
            page_cache.insert(0, page_cache.pop(index))
            return 200, cached_page  # only 200 responses are cached

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36",
    }
    async with aiohttp.ClientSession(headers=headers) as session:
        async with session.get(url) as response:
            # BeautifulSoup parsing is somewhat resource intensive,
            # so we pass that to another thread to avoid blocking the rest of the asyncio events
            soup = await asyncio.to_thread(
                bs4.BeautifulSoup,
                await response.text(),
                "html.parser",
            )

            # add to cache
            if response.status == 200:
                page_cache.insert(0, (url, soup))
                while len(page_cache) > PAGE_CACHE_SIZE:
                    page_cache.pop()

            return response.status, soup


async def search_oxford_dictionary(word: str) -> tuple[str, int, bs4.BeautifulSoup]:
    """
    Fetches the Oxford Learner's Dictionary page for the provided word.

    :param word: the word whose page should be fetched
    :return: the url, the http status code, and the parsed page content (using BeautifulSoup)
    """
    path = re.sub(r"\s+", r"-", word.lower().strip())
    url = f"https://www.oxfordlearnersdictionaries.com/definition/english/{urllib.parse.quote(path)}"
    return url, *await fetch_page_cached(url)


def parse_oxford_suggestions_page(soup: bs4.BeautifulSoup) -> list[str]:
    """
    Parses the 404 page and returns all of the suggestions provided there.

    :param soup: the parsed 404 page
    :return: a list of suggestions
    """
    return [result.text for result in soup.select(".result-list > li")]


def parse_oxford_definition_page(url: str, soup: bs4.BeautifulSoup) -> WordInformation:
    """
    Parses the provided oxford definition page.
    Should only call this method after receiving a 200 status code.
    Raises a ValueError if the page format is unfamiliar.

    :param url: the url of the definition page
    :param soup: the BeautifulSoup-parsed page
    :return: a WordInformation
    """

    if headword_element := soup.select_one(".webtop > .headword"):
        word = headword_element.text.strip()
    else:
        msg = "Failed to find word via selector `.webtop > .headword`"
        raise ValueError(msg)

    if us_pronunciation_element := soup.select_one(".webtop > .phonetics .phons_n_am"):
        us_pronunciation = Pronunciation.parse_from_oxford_phonetic_element(
            us_pronunciation_element,
        )
    else:
        us_pronunciation = None

    if gb_pronunciation_element := soup.select_one(".webtop > .phonetics .phons_n_am"):
        gb_pronunciation = Pronunciation.parse_from_oxford_phonetic_element(
            gb_pronunciation_element,
        )
    else:
        gb_pronunciation = None

    if part_of_speech_element := soup.select_one(".webtop > .pos"):
        part_of_speech = part_of_speech_element.text.strip()
    else:
        part_of_speech = None

    similar_words: list[SimilarWord] = []
    if related_entries_list := soup.select_one("#relatedentries ul"):
        for similar_word_element in related_entries_list.select("li:not(.more)"):
            if not (anchor_element := similar_word_element.select_one("a")):
                continue
            if not anchor_element.has_attr("href"):
                continue
            similar_word_page = anchor_element["href"]
            assert isinstance(similar_word_page, str)

            similar_word = similar_word_element.text
            if pos_element := similar_word_element.select_one("pos"):
                similar_part_of_speech = pos_element.text.strip()
                similar_word = (
                    similar_word.strip().removesuffix(similar_part_of_speech).strip()
                )
            else:
                similar_part_of_speech = None

            similar_words.append(
                SimilarWord(
                    word=similar_word,
                    part_of_speech=similar_part_of_speech,
                    url=similar_word_page,
                ),
            )

    senses: list[Sense] = []
    for sense_element in soup.select(".sense"):
        if definition_element := sense_element.select_one(".def"):
            definition = definition_element.text.strip()
        else:
            continue

        if grammar_element := sense_element.select_one(".grammar"):
            grammar = grammar_element.text.strip()
        else:
            grammar = None

        if labels_element := sense_element.select_one(".labels"):
            labels = labels_element.text.strip()
        else:
            labels = None

        examples: list[Example] = []
        for example_element in sense_element.select(".examples > li"):
            if sentence_element := example_element.select_one(".x"):
                sentence = sentence_element.text.strip()
            else:
                continue

            if labels_element := example_element.select_one(".labels"):
                labels = labels_element.text.strip()
            else:
                labels = None

            examples.append(
                Example(
                    labels=labels,
                    sentence=sentence,
                ),
            )

        senses.append(
            Sense(
                definition=definition,
                grammar=grammar,
                labels=labels,
                examples=examples,
            ),
        )

    if not senses:
        msg = "Failed to find a single definition on the page via selector `.sense`"
        raise ValueError(
            msg,
        )

    return WordInformation(
        url=url,
        word=word,
        us_pronunciation=us_pronunciation,
        gb_pronunciation=gb_pronunciation,
        part_of_speech=part_of_speech,
        senses=senses,
        similar_words=similar_words,
    )


async def search(word: str) -> WordInformation | list[str]:
    """
    Searches for a certain word in the Oxford Learner's Dictionary, and parses the result into a WordInformation.
    If the word was not found, returns a list of valid suggestions.

    :param word: the word you would like to search for
    :param result_index: which version of the word you would like to select
    :return: a WordInformation if the word was found in the dictionary, and a list of suggested words otherwise.
    """
    url, status_code, soup = await search_oxford_dictionary(word)

    if status_code == 404:
        return parse_oxford_suggestions_page(soup)
    if status_code == 200:
        return parse_oxford_definition_page(url, soup)

    msg = f"Unexpected status code {status_code} while searching for word {word!r}"
    raise Exception(
        msg,
    )


def ChooseSimilarWordView(
    ctx: ApplicationContext,
    word_info: WordInformation,
) -> discord.ui.View:
    """
    Generates a dropdown menu View that allows you to select a similar word to define.

    :param ctx: the current ApplicationContext
    :param word_info: a WordInformation pertaining to the current interaction
    :return: an instance of a subclass of `discord.ui.View`
    """

    class View(discord.ui.View):
        @discord.ui.select(
            placeholder=f"{word_info.word} - {word_info.part_of_speech}",
            options=[
                discord.SelectOption(
                    label=word_info.word,
                    description=word_info.part_of_speech,
                    value="current_word",
                    default=True,
                ),
            ]
            + [
                discord.SelectOption(
                    label=similar_word.word,
                    description=similar_word.part_of_speech,
                    value=f"similar_word_{index}",
                )
                for index, similar_word in enumerate(word_info.similar_words)
            ],
        )
        async def select_callback(
            self,
            select: discord.ui.Select,
            interaction: discord.Interaction,
        ) -> None:  # the function called when the user is done selecting options
            value = select.values[0]
            if value == "current_value":
                # do nothing
                await interaction.response.defer()
                return

            assert isinstance(value, str)
            index = int(value.removeprefix("similar_word_"))

            similar_word = word_info.similar_words[index]
            new_word_info = await similar_word.fetch()

            # It is annoying to have the dropdown list change after selecting a new word,
            # so copy over the existing similar words.
            new_word_info.similar_words = word_info.similar_words.copy()
            del new_word_info.similar_words[index]
            new_word_info.similar_words.insert(
                0,
                SimilarWord(
                    url=word_info.url,
                    word=word_info.word,
                    part_of_speech=word_info.part_of_speech,
                ),
            )

            await ctx.edit(
                embed=new_word_info.build_embed(),
                view=ChooseSimilarWordView(ctx, new_word_info),
            )

            await interaction.response.defer()

    return View()


class Dictionary(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @commands.slash_command(name="define", description="Defines a word.")
    @option("word", str, description="The word to define.", required=True)
    @limit(2)
    async def define(self, ctx: ApplicationContext, word: str) -> None:
        """
        It takes a word as an argument, and returns the definition of that word

        :param ctx: the current ApplicationContext
        :param word: the word to define
        :return: None. Replies to the Discord interaction with information about the word.
        """
        await ctx.defer()
        word_info = await search(word)

        if not isinstance(word_info, WordInformation):
            suggestions = word_info
            embed = EmbedBuilder(
                title=f"Unknown Word __**{word}**__",
                description="The Oxford Learner's Dictionary does not contain that word.",
                color=0xFF0000,  # RED
                fields=[("Suggestions", "\n".join(suggestions), True)],
            ).build()
            # not ephemeral so people can still use this command to prove the nonexistence of a word
            await ctx.respond(embed=embed)
            return

        if word_info.similar_words:
            view = ChooseSimilarWordView(ctx, word_info)
        else:
            view = None

        await ctx.edit(embed=word_info.build_embed(), view=view)
        Log("$ used the dictionary command", ctx.author)


def setup(bot: commands.Bot) -> None:
    bot.add_cog(Dictionary(bot))
