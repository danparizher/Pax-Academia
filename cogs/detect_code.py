from contextlib import suppress
from itertools import islice
from os import getenv

import discord
from discord.ext import commands

from cogs.tips import send_tip
from util import code_detection
from util.embed_builder import EmbedBuilder
from util.Logging import Log


class DetectCode(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.cs_category_id = int(getenv("UNFORMATTED_CODE_DETECTION_CATEGORY_ID", -1))

    @staticmethod
    def format_detected_code(
        language: str,
        sections: tuple[code_detection.DetectedSection, ...],
    ) -> str:
        return "\n".join(
            f"```{language}\n{section.text}\n```" if section.is_code else section.text
            for section in sections
        )

    @staticmethod
    def get_first_lines_of_code(
        sections: tuple[code_detection.DetectedSection, ...],
        n: int = 3,
    ) -> str:
        """
        Just gets the first N lines of code from the provided sections.
        """
        code_generator = (
            line
            for section in sections
            for line in section.lines
            if section.is_code and line and not line.isspace()
        )
        return "\n".join(islice(code_generator, n))

    @classmethod
    def get_formatting_example(
        cls, language: str, sections: tuple[code_detection.DetectedSection, ...]
    ) -> tuple[str, str]:
        r"""
        Returns two versions of a string. The first has all special characters escaped, like so:
        \`\`\`py
        variable\_name = 1 + 2 \* 3
        print("variable\_name")
        \`\`\`

        and the second will have working formatting, like so:
        ```py
        variable_name = 1 + 2 * 3
        print("variable_name")
        ```

        such that the first string can be copy/pasted out of discord to create the second string
        """
        code = cls.get_first_lines_of_code(sections)
        escaped_code = (
            code.replace("\\", "\\\\").replace("*", "\\*").replace("_", "\\_")
        )
        return (
            f"\\`\\`\\`{language}\n{escaped_code}\n\\`\\`\\`",
            f"```{language}\n{code}\n```",
        )

    @staticmethod
    def likely_contains_code(text: str) -> bool:
        """
        A simple algorithm to generically detect code-like features of a message.
        """
        minimum_code_probability = 0.5

        lines = text.splitlines()

        # Most people don't paste one line of code, so this avoids false positives
        if len(lines) == 1:
            return False

        non_blank_lines = [line for line in lines if line.strip()]
        code_like_lines = [
            line
            for line in non_blank_lines
            if any(
                [
                    line.startswith("  "),
                    line.endswith((";", "{", "}", "]", "[", ")", "(", ":", ",")),
                ],
            )
        ]

        # Calculate the percentage of code-like lines
        percentage_code_like = (
            len(code_like_lines) / len(non_blank_lines) if non_blank_lines else 0
        )

        return percentage_code_like >= minimum_code_probability

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message) -> None:
        if (
            message.author.bot
            or not isinstance(message.channel, discord.TextChannel)
            or message.channel.category is None
            or message.channel.category.id != self.cs_category_id
            or "```" in message.content
        ):
            return

        if detection_result := code_detection.detect(message.content):
            language, sections = detection_result
            escaped, unescaped = self.get_formatting_example(language, sections)

            embed = EmbedBuilder(
                title="Auto-Formatted Code",
                description=self.format_detected_code(language, sections),
                color=0x32DC64,  # same green as tips
            ).build()

            await message.reply(
                (
                    "I've detected that you have unformatted code, which is difficult to read.\n"
                    "You can format code by surrounding it with backticks `` ``` `` (not quotes `'''`).\n"
                    "\n"
                    "For example, this message:\n"
                    f"{escaped}\n"
                    "\n"
                    "will look like this:\n"
                    f"{unescaped}\n"
                    "\n"
                    "Below, I have automatically applied that formatting for you."
                ),
                embed=embed,
            )

        # if language-specific algorithms fail, use a generic algorithm
        # TODO: maybe remove this once we're confident w/ our language-specific algorithms
        elif self.likely_contains_code(message.content):
            await send_tip(message.channel, "Format Your Code", message.author, "bot")
            with suppress(AttributeError):
                Log(
                    f" $ sent potential code in {message.channel.name}, bot responded with tip",
                    message.author,
                )


def setup(bot: commands.Bot) -> None:
    bot.add_cog(DetectCode(bot))
