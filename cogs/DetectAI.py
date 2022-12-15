import os

import discord
from discord import option
from discord.ext import commands
from playwright.async_api import async_playwright


class AI(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @commands.slash_command(
        name="detectai", description="Runs text through an AI detector."
    )
    @option(
        "text",
        str,
        description="The text to run through the AI.",
        required=True,
    )
    async def ai(self, ctx: commands.Context, text: str) -> None:
        """
        It takes a string, goes to a website, fills in a text box, clicks a button, waits for a certain
        element to appear, takes a screenshot of the element, sends the screenshot to the channel, and
        deletes the screenshot
        
        :param ctx: commands.Context - The context of the command
        :type ctx: commands.Context
        :param text: str
        :type text: str
        """
        await ctx.defer()
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context()
            page = await context.new_page()
            await page.goto("http://gltr.io/dist/index.html")
            await page.fill("textarea", text)
            await page.click("button")
            await page.wait_for_selector("text=top k count")
            await page.locator("#all_result").screenshot(
                path=f"util/screenshot_{ctx.author.id}.png"
            )
            await browser.close()
            await ctx.respond(file=discord.File(f"util/screenshot_{ctx.author.id}.png"))
            os.remove(f"util/screenshot_{ctx.author.id}.png")


def setup(bot: commands.Bot) -> None:
    bot.add_cog(AI(bot))
