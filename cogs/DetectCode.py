import discord
from discord.ext import commands
from discord.commands.context import ApplicationContext
from cogs.Tips import send_tip


class CodeDetector(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.cs_category_id = 1137609015573106728  # Replace with actual category ID

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message) -> None:
        if (
            not message.author.bot
            and message.channel.category.id == self.cs_category_id
            and not message.content.startswith("```")
        ):
            # Set the threshold for what percentage of lines should start with indentation
            # You can adjust this value based on your preferences
            indentation_threshold = 0.5

            lines = message.content.split("\n")

            # Most people don't paste one line of code, so this avoids false positives
            if len(lines) == 1:
                return

            non_blank_lines = [line for line in lines if line.strip()]
            code_like_lines = [
                line
                for line in non_blank_lines
                if any(
                    [
                        line.startswith(("    ", "  ")),
                        line.endswith((";", "{", "}", "]", "[", ")", "(", ":", ",")),
                    ]
                )
            ]

            # Calculate the percentage of code-like lines
            percentage_code_like = (
                len(code_like_lines) / len(non_blank_lines) if non_blank_lines else 0
            )

            if percentage_code_like >= indentation_threshold:
                await send_tip(
                    message.channel, "Format Your Code", message.author, "yes"
                )


def setup(bot: commands.Bot) -> None:
    bot.add_cog(CodeDetector(bot))
