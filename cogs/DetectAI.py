import asyncio
import io

import discord
from discord import option
from discord.ext import commands
from playwright.async_api import async_playwright

from util.EmbedBuilder import EmbedBuilder


class AI(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @commands.slash_command(
        name="detect-ai",
        description="Runs text through an AI detector.",
    )
    @option(
        "text",
        str,
        description="The text to run through the AI.",
        required=True,
    )
    @option(
        "ephemeral",
        bool,
        description="Whether the response should be ephemeral or not. Only staff can make this False.",
        required=False,
        default=True,
    )
    async def ai(self, ctx: commands.Context, text: str, ephemeral: bool) -> None:
        """
        It opens a headless browser, goes to the website, fills in the text, clicks the button, waits for
        the result, takes a screenshot of the result, closes the browser, and sends the screenshot to the
        channel

        :param ctx: commands.Context - The context of the command
        :type ctx: commands.Context
        :param text: str
        :type text: str
        """
        if "Staff" not in [role.name for role in ctx.author.roles]:
            ephemeral = True
        await ctx.defer(ephemeral=ephemeral)

        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=False)
                context = await browser.new_context()
                page = await context.new_page()
                await page.set_extra_http_headers(
                    {
                        "Accept-Language": "en-US,en;q=0.9",
                        "Accept-Encoding": "gzip, deflate, br",
                        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
                        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.3987.149 Safari/537.36",
                    },
                )
                await page.goto("https://app.copyleaks.com/v1/scan/ai/embedded")
                await page.fill("textarea", text)
                await page.click("button")
                # Pass the cloudflare challenge by clicking the checkbox
                # <iframe src="https://challenges.cloudflare.com/cdn-cgi/challenge-platform/h/b/turnstile/if/ov2/av0/ltitq/0x4AAAAAAADZUXiboAFN3tU8/light/normal" allow="cross-origin-isolated" id="cf-chl-widget-ltitq" tabindex="0" title="Widget containing a Cloudflare security challenge" style="border: none; overflow: hidden; width: 300px; height: 65px;"></iframe>
                try:
                    await page.click("input#cf-chl-accept")
                except Exception:
                    await asyncio.sleep(999)
                # Wait for page to finish changing after clicking the button
                # <div _ngcontent-ng-universal-copyleaks-c280 class="scan-text-editor scan-text-editor-result ng-tns-c280-0 ng-star-inserted">
                await page.wait_for_selector(
                    "div.scan-text-editor.scan-text-editor-result"
                )
                screenshot = await page.locator("textarea").screenshot()
                await browser.close()
                await ctx.respond(
                    embed=EmbedBuilder(
                        title="AI Detector",
                        description="Here is the result of running the text through the AI detector:",
                    ).build(),
                    file=discord.File(io.BytesIO(screenshot), filename="result.png"),
                    ephemeral=ephemeral,
                )
        except Exception as e:
            await ctx.respond(
                embed=EmbedBuilder(
                    title="Error",
                    description=f"An error occurred while running the command:\n\n{e}",
                ).build(),
                ephemeral=True,
            )


def setup(bot: commands.Bot) -> None:
    bot.add_cog(AI(bot))
