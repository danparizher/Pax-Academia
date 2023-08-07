from discord import Member, option
from discord.abc import Messageable
from discord.commands.context import ApplicationContext
from discord.ext import commands

from util.EmbedBuilder import EmbedBuilder
from util.Logging import Log, limit

TIPS = {
    "Ask Your Question": (
        "You can be helped sooner if you simply ask your question instead of "
        "asking if you can ask a question or if anyone is available to help you.\n\n"
        "Instead of asking "
        '"Does anyone know X?", "Can someone help me with Y?", or "Are there any experts in Z?" '
        "just ask your question or describe your problem directly."
    ),
    "Format Your Code": (
        "Your code is difficult to read. Format your code so that people can read it.\n"
        "You can format code on discord by using 3 backticks `` ``` `` (**not** quotes `'''`) "
        "followed by the name of the computer language. So to format Python code, it would be `` ```python``.\n\n"
        "Here's a complete example of how to format Java code.\n\n"
        "This message:\n"
        "**\\`\\`\\`java\n"
        'System.out.println("Code formatting is neat!");\n'
        "\\`\\`\\`**\n\n"
        "Will look like this:\n"
        "```java\n"
        'System.out.println("Code formatting is neat!");\n'
        "```\n"
        "Go ahead, try it! You can copy/paste the message above."
    ),
    "Let Us Know What You've Already Tried": (
        "Please show and describe the steps you've already completed so that we may assist you further.\n"
        "This way, we can start helping you right where you left off and can save everyone's time."
    ),
    "Use the Mention System": (
        "If some time has passed and nobody is responding to your question, then you can use "
        " the `/mention create [role]` command to mention everyone with the relevant role, such as @Math or @Biology.\n\n"
        "You can select a certain message to mention for by right clicking on a message and selecting Apps -> mention.\n\n"
        "After waiting 10 minutes, you can use the `/mention send` which will ping the role with your message.\n\n"
        "If you decide to cancel your request, you can use `/mention cancel`, or if you want to create a different "
        "mention you can use `/mention overwrite [role]` which works similarly to `/mention create [role]`."
    ),
    "Try Googling It": (
        "There are many resources available online, so googling your problem should be the first course of action.\n"
        "Very frequently, you can get an answer more quickly and with more detail.\n"
        "If you've already tried googling the problem, then let us know what you found and why it wasn't sufficient!"
    ),
}


async def send_tip(
    ctx: Messageable,
    tip: str,
    ping: Member | None = None,
    anonymous: str = "No",
    use_embed: bool = True,
) -> None:
    if not isinstance(ctx, ApplicationContext):
        message_method = ctx.send
    elif anonymous.casefold() == "no":
        message_method = ctx.respond
    else:
        message_method = ctx.send
        await ctx.respond(
            "Thanks for the tip! It will be sent anonymously.",
            ephemeral=True,
            delete_after=5,
        )

    if use_embed:
        embed = EmbedBuilder(
            title=f"Tip: {tip}.",
            description=TIPS[tip],
            color=0x32DC64,  # a nice pastel green
        ).build()

        await message_method(
            ping.mention if ping else None,
            embed=embed,
        )
    else:
        await message_method(
            f"{ping.mention + ' ' if ping else ''}**{tip}**\n\n{TIPS[tip]}",
        )


class Tips(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @commands.slash_command(name="tip", description="Sends various homework-help tips.")
    @option(
        name="tip",
        description="The tip to send.",
        type=str,
        choices=TIPS,
        required=True,
    )
    @option(
        name="ping",
        description="Who should be pinged with the tip?",
        type=Member,
        required=False,
    )
    @option(
        name="anonymous",
        description="Should the tip be sent anonymously?",
        type=str,
        choices=["Yes", "No"],
        required=False,
    )
    @option(
        name="embed",
        description="Should the tip be sent in an embed?",
        type=str,
        choices=["Yes", "No"],
        required=False,
    )
    @limit(3)
    async def tip(
        self,
        ctx: ApplicationContext,
        tip: str,
        ping: Member | None = None,
        anonymous: str = "No",
        embed: str = "Yes",
    ) -> None:
        await send_tip(ctx, tip, ping, anonymous, embed.casefold() == "yes")
        Log(f"$ used tip: {tip} | in channel {ctx.channel.name}", ctx.author)


def setup(bot: commands.Bot) -> None:
    bot.add_cog(Tips(bot))
