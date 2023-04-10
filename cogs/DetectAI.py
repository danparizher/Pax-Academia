import io

import discord
import undetected_chromedriver as uc
from discord import option
from discord.ext import commands
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

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
        if not isinstance(ctx.channel, discord.TextChannel):
            return
        if not ctx.channel.category or not ctx.channel.category.name.lower().endswith(
            "help",  # right now, it'll just say "The application did not respond" if you try to run it in a non-help channel
        ):
            return
        if "Staff" not in [
            role.name for role in ctx.author.roles
        ] and not ctx.channel.category.name.lower().endswith("help"):
            ephemeral = True
        await ctx.defer(ephemeral=ephemeral)

        try:
            options = uc.ChromeOptions()
            options.add_argument("--headless")
            driver = uc.Chrome(options=options)
            driver.get("https://app.copyleaks.com/v1/scan/ai/embedded")
            driver.find_element(By.CSS_SELECTOR, "textarea").send_keys(text)
            driver.find_element(By.CSS_SELECTOR, "button").click()
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, "div.scan-text-editor-result"),
                ),
            )
            screenshot = driver.get_screenshot_as_png()
            driver.quit()
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
