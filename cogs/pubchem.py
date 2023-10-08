from __future__ import annotations

import asyncio
import string

import pubchempy as pcp
from discord import ApplicationContext, option
from discord.ext import commands

from message_formatting.embeds import EmbedBuilder
from util.limiter import limit
from util.logger import log


class CompoundNotFoundException(Exception):
    pass


def fetch_compound(name: str) -> pcp.Compound:
    """
    It takes a string as an argument, and returns a Compound.

    :param name: The name of the compound you want to get data for
    :type name: str
    :return: Compound
    """
    compounds = pcp.get_compounds(name, "name")
    if not compounds:
        raise CompoundNotFoundException

    compound = compounds[0]
    assert isinstance(
        compound,
        pcp.Compound,
    ), "pubchempy only converts to another format if we specifically request it."

    return compound


class PubChem(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    def to_subscript(self, number: str) -> str:
        """
        It takes a number and returns a string with the number's digits replaced by their subscript
        equivalents

        :param number: int
        :type number: int
        :return: The subscripted version of the number.
        """
        return number.translate(str.maketrans(string.digits, "₀₁₂₃₄₅₆₇₈₉"))

    @commands.slash_command(
        name="chemsearch",
        description="Searches the database for a compound.",
    )
    @option(
        "name",
        str,
        description="The name of the compound to be searched.",
        required=True,
    )
    @limit(2)
    async def pubchem(self, ctx: ApplicationContext, name: str) -> None:
        """
        It takes a string, searches for it on PubChem, and returns a Discord embed with the results

        :param ctx: commands.Context
        :type ctx: commands.Context
        :param name: str
        :type name: str
        """
        try:
            compound = await asyncio.to_thread(fetch_compound, name)
            embed = EmbedBuilder(
                title=f"Properties of __{name.title()}__",
                url=f"https://pubchem.ncbi.nlm.nih.gov/compound/{compound.cid}",
                description=f"**IUPAC Name:**\n{compound.iupac_name}",
                fields=[
                    (
                        "Molecular Formula",
                        self.to_subscript(str(compound.molecular_formula)),
                        True,
                    ),
                    (
                        "Exact Mass",
                        str(round(float(str(compound.exact_mass)), 2)),
                        True,
                    ),
                    ("Charge", str(compound.charge), True),
                    ("Molecular Weight", str(compound.molecular_weight), True),
                    ("XLogP", str(compound.xlogp), True),
                    ("TPSA", str(compound.tpsa), True),
                    ("Complexity", str(compound.complexity), True),
                ],
                image=f"https://pubchem.ncbi.nlm.nih.gov/image/imagefly.cgi?cid={compound.cid}&width=400&height=400",
            ).build()

            await ctx.respond(embed=embed)

            log(f"Chemsearch command used by $ in {ctx.guild}.", ctx.author)

        except CompoundNotFoundException:
            embed = EmbedBuilder(
                title="Error",
                description=f"Compound **{name.title()}** not found. Did you spell it correctly?",
            ).build()

            await ctx.respond(embed=embed, ephemeral=True)


def setup(bot: commands.Bot) -> None:
    bot.add_cog(PubChem(bot))
