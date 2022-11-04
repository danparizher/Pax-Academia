import os

import aiohttp
import discord
import pubchempy as pcp
from discord.ext import commands
from discord import option
from util.EmbedBuilder import EmbedBuilder
from util.Logging import log


async def get_cid(name: str) -> tuple:
    compound = pcp.get_compounds(name, "name")[0]
    return compound.cid


async def get_structure(name: str) -> None:
    compound = pcp.get_compounds(name, "name")[0]
    return compound.molecular_formula


async def draw(cid: int) -> None:
    async with aiohttp.ClientSession() as session:
        async with session.get(
            f"https://pubchem.ncbi.nlm.nih.gov/image/imagefly.cgi?cid={cid}&width=400&height=400"
        ) as resp:
            with open("molecule.png", "wb") as f:
                f.write(await resp.read())


class PubChem(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @commands.slash_command(
        name="chemsearch", description="Searches PubChem for a compound."
    )
    @option(
        name="name",
        description="The name of the compound to be searched.",
        required=True,
    )
    async def pubchem(self, ctx: commands.Context, name: str) -> None:
        try:
            cid = await get_cid(name)
            formula = await get_structure(name)
            await draw(cid)
            embed = EmbedBuilder(
                title=f"Chemical Composition of __{name.capitalize()}__",
                description=f"Molecular Formula: {formula}",
                image="attachment://molecule.png",
            ).build()

            await ctx.respond(embed=embed, file=discord.File("molecule.png"))
            os.remove("molecule.png")

            log(f"Chemsearch command used by {ctx.author} in {ctx.guild}.")

        except Exception as e:
            log(
                f"An error occurred while gathering data for **{name.capitalize()}**:\n\n{e}"
            )


def setup(bot: commands.Bot) -> None:
    bot.add_cog(PubChem(bot))
