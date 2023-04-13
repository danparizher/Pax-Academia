import contextlib
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
    async def ai(self, ctx: commands.Context, text: str) -> None:
        """
        Runs a given text through an AI detector and returns the result as an image.

        :param ctx: The context of the command, which includes information about the user, channel, and
        server where the command was invoked
        :type ctx: commands.Context
        :param text: The text that will be analyzed by the AI detector
        :type text: str
        :param ephemeral: A boolean parameter that determines whether the response message should only be
        visible to the user who triggered the command (True) or visible to everyone in the channel (False)
        :type ephemeral: bool
        :return: The function is not returning anything, it is using the `await` keyword to send responses
        to the user in the Discord chat.
        """
        if not isinstance(ctx.channel, discord.TextChannel):
            return
        if not ctx.channel.category or not ctx.channel.category.name.lower().endswith(
            "help",
        ):
            await ctx.respond(
                embed=EmbedBuilder(
                    title="Error",
                    description="This command can only be run in a help channel.",
                ).build(),
                ephemeral=True,
            )
            return

        if len(text) < 150:
            await ctx.respond(
                embed=EmbedBuilder(
                    title="Error",
                    description="You must enter at least 150 characters.",
                ).build(),
                ephemeral=True,
            )
            return

        await ctx.defer(ephemeral=True)

        try:
            options = uc.ChromeOptions()
            options.add_argument("--headless")
            driver = uc.Chrome(options=options)
            driver.get("https://app.copyleaks.com/v1/scan/ai/embedded")
            driver.find_element(By.CSS_SELECTOR, "textarea").send_keys(text)
            driver.find_element(By.CSS_SELECTOR, "button").click()
            with contextlib.suppress(Exception):
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located(
                        (
                            By.XPATH,
                            "/html/body/app-root/div/app-scan-inline-widget-layout/app-error-page/div/div/span/div/b",
                        ),
                    ),
                )
                driver.quit()
                await ctx.respond(
                    embed=EmbedBuilder(
                        title="Error",
                        description="You have reached your limit for the day. Please try again tomorrow.",
                    ).build(),
                    ephemeral=True,
                )
                return
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, "div.scan-text-editor-result"),
                ),
            )
            screenshot = driver.get_screenshot_as_png()
            driver.quit()

            await ctx.respond(
                file=discord.File(io.BytesIO(screenshot), filename="result.png"),
                ephemeral=True,
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
