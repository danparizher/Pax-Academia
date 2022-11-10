import discord
from discord.commands import option
from discord.ext import commands

from util.EmbedBuilder import EmbedBuilder
from util.Logging import log

rules = {
    "Rule A): Respect": "Maintain civility and conduct yourself appropriately. Avoid derogatory language, discriminatory jokes, and hate speech.",
    "Rule B): Staff Report": "Use the staff report feature for reporting rule violations only.",
    "Rule C): Backseat Moderating": "To avoid conflicts, simply use the `@Staff Report` ping or `/report` to report rule breakers.",
    "Rule D): Age requirement": "You must be at least thirteen (13) years old to use Discord and to be in this server.",
    "Rule E): DM (Direct Message) policy": "As a courtesy to others, do not send direct messages for the purpose of receiving help or advertising without receiving permission.",
    "Rule F): Paywalls, subscription services": "Do not ask other users to share accounts or violate paywalls for services such as Chegg or Course Hero.",
    "Rule G): Clean content": "No not safe for work (NSFW), illegal, or unsightly content in messages, nicknames, or avatars.",
    "Rule H): English requirement outside language channels": "To make moderation easier, only English discussions are allowed. This rule is waived in the Language Help channels and may be waived in exceptional circumstances [as directed by Staff].",
    "Rule I): Advertising": "Do not advertise servers, social media, services, sites, or products, including exchanges for having work done.",
    "Rule J): Academic integrity, cheating": "Do not attempt to cheat on exams, papers, or assignments.",
    "Rule K): Trolling in help channels, bad faith responses": "The purpose of this server is to discuss academic topics. Do not provide bad faith responses to questions or requests. Additionally, if you don't have anything useful to say, don't say it.",
    "Rule L): Mentioning": "You must include your question in the mention and only use it once per question (e.g. use ?mention directly after you ask your question). Include specific questions, not vague or unanswerable ones. Use the proper role(s) that pertain to your question.",
    "Rule M): Spamming": "Do not send repeating messages, messages in quick succession, or reactions to a message needlessly. If a help mention (ping) is used, do not send messages unless it meaningfully contributes to the channel. Post your question in only one channel.",
}


def get_rules() -> list[str]:
    return rules.keys()


class Rules(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @commands.slash_command(name="rule", description="Show server rules.")
    @option(
        "rule", str, description="The rule to show.", required=True, choices=get_rules()
    )
    @option("user", discord.User, description="The user to ping.", required=False)
    async def rule(self, ctx: commands.Context, rule: str, user: discord.User) -> None:
        embed = EmbedBuilder(title=rule, description=rules[rule]).build()

        await ctx.respond(content=f"<@{user.id}>" if user else None, embed=embed)

        log(f"Rule command used by {ctx.author} in {ctx.guild}.")


def setup(bot: commands.Bot) -> None:
    bot.add_cog(Rules(bot))
