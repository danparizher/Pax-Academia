import pubchempy as pcp
from discord.ext import commands
from discord import option
from util.EmbedBuilder import EmbedBuilder
from util.Logging import log


async def get_data(name: str) -> dict:
    compound = pcp.get_compounds(name, "name")
    return {
        "cid": compound[0].cid,
        "formula": compound[0].molecular_formula,
    }


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
            data = await get_data(name)
            embed = EmbedBuilder(
                title=f"Properties of __{name.title()}__",
                description=f"Molecular Formula: {data['formula']}",
                image=f"https://pubchem.ncbi.nlm.nih.gov/image/imagefly.cgi?cid={data['cid']}&width=400&height=400",
            ).build()

            await ctx.respond(embed=embed)

            log(f"Chemsearch command used by {ctx.author} in {ctx.guild}.")

        except Exception as e:
            log(
                f"An error occurred while gathering data for **{name.title()}**:\n\n{e}"
            )


def setup(bot: commands.Bot) -> None:
    bot.add_cog(PubChem(bot))
