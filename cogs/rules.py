from __future__ import annotations

import discord
from discord.commands import option
from discord.ext import commands

from message_formatting.embeds import EmbedBuilder
from util.limiter import limit
from util.logger import log

rules = {
    "Rule A): Respect": "Maintain civility and conduct yourself appropriately. Avoid derogatory language, discriminatory jokes, and hate speech.",
    "Rule B): `@Staff Report` and `/report` mention": "Use for reporting rule violations only.",
    "Rule C): Backseat Moderating": "To avoid conflicts, simply use the `@Staff Report` ping or `/report` to report rule breakers.",
    "Rule D): Age Requirement": "You must be at least thirteen (13) years old to use Discord and to be in this server.",
    "Rule E): Unsolicited Direct Messages": "As a courtesy to others, do not send direct messages for the purpose of receiving help or advertising without receiving permission.",
    "Rule F): Bypassing Paywalled Accounts and Copyrights": "Do not ask other users to share accounts or violate paywalls for services such as Chegg or Course Hero. This includes asking others to share digital versions of books and other copyrighted material which you have not received appropriate permission to distribute.",
    "Rule G): Clean Content": "No not safe for work (NSFW), illegal, or unsightly content in messages, nicknames, the about me section, or avatars.",
    "Rule H): English Only": "To make moderation easier, only English discussions are allowed. This rule is waived in the Language Help channels and may be waived in exceptional circumstances [as directed by Staff].",
    "Rule I): Advertising": "Do not advertise servers, social media, services, sites, or products, including exchanges (e.g. but not limited to money or nitro) for having work done. This includes asking others to pay you for your help.",
    "Rule J): Maintain Academic Integrity": "Do not attempt to cheat on exams, papers, or assignments. Additionally, the server is not here to do your work for you. If possible provide guidance, instead of giving direct answers.",
    "Rule K): Keep it Pertinent and Positive in Help Channels": "The purpose of this server is to discuss academic topics. Do not provide bad-faith responses to questions or requests. Additionally, if you have nothing useful to say, don't say it.",
    "Rule L): Mentioning": "You must include your question in the mention and only use it once per question (e.g. use `?mention` directly after you ask your question). Include specific questions, not vague or unanswerable ones. Use the proper role(s) that pertain to your question.",
    "Rule M): Spamming and Multiposting": "Do not send repeating messages, messages in quick succession, or reactions to a message needlessly. If a help mention (ping) is used, do not send messages unless it meaningfully contributes to the channel.",
    "Rule N): Be Yourself When Helping": "Helpers are expected to provide their own original responses and thoughts. Providing answers to questions using responses produced by or based on output by ChatGPT or other generative language models is strictly prohibited. Violators will face an extended mute or be banned from the server.",
    "Rule O): Help in Help Channels": "We are a free help server and want to provide help for everyone free of charge. When someone asks a question in a public channel or forum, please answer their question there and do not offer to take it to DMs if the poster didn't *explicitly* ask for it. This is to prevent ill-intended actors from offering monetary services which we strictly do not want to facilitate in any way.",
    "Rule P): Single Posting": "Please post your question in only one channel. This prevents redundancy and allows helpers to more easily identify questions which haven't been answered yet. If you would like to ask your question in another channel, please delete the original post and then ask your question in the other channel.",
    "Rule Q): Personal Information": "Do not post screenshots, images, messages or any other content that includes personal information of another person if this information is not in the public domain (etc. on a public website).",
    "Rule R): Non-message behavior": "The above rules extend to any form of expression on the server, including but not limited to names, profile pictures, status and the about me section.",
}


class Rules(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @commands.slash_command(name="rule", description="Show server rules.")
    @option(
        "rule",
        str,
        description="The rule to show.",
        required=True,
        choices=rules.keys(),
    )
    @option("user", discord.User, description="The user to ping.", required=False)
    @limit(3)
    async def rule(
        self,
        ctx: discord.ApplicationContext,
        rule: str,
        user: discord.User,
    ) -> None:
        embed = EmbedBuilder(title=rule, description=rules[rule]).build()

        await ctx.respond(content=f"<@{user.id}>" if user else None, embed=embed)

        log(f"Rule command used by $ in {ctx.guild}.", ctx.author)


def setup(bot: commands.Bot) -> None:
    bot.add_cog(Rules(bot))
