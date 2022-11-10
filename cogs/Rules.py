import discord
from discord.commands import option
from discord.ext import commands

from util.EmbedBuilder import EmbedBuilder
from util.Logging import log


rules = {
    "respect": "Maintain civility and conduct yourself appropriately. Avoid derogatory language, discriminatory jokes, and hate speech.",
    "staff-reporting": "Use the staff report feature for reporting rule violations only.",
    "backseat-moderating": "To avoid conflicts, simply use the \`@Staff Report\` ping or \`/report\` to report rule breakers.",
    "underage": "You must be at least thirteen (13) years old to use Discord and to be in this server.",
    "unsolicited-dm": "As a courtesy to others, do not send direct messages for the purpose of receiving help or advertising without receiving permission.",
    "paywalls": "Do not ask other users to share accounts or violate paywalls for services such as Chegg or Course Hero.",
    "clean-content": "No not safe for work (NSFW), illegal, or unsightly content in messages, nicknames, or avatars.",
    "english-only": "To make moderation easier, only English discussions are allowed. This rule is waived in the Language Help channels and may be waived in exceptional circumstances [as directed by Staff].",
    "advertising": "Do not advertise servers, social media, services, sites, or products, including exchanges for having work done.",
    "academic-integrity": "Do not attempt to cheat on exams, papers, or assignments.",
    "bad-faith": "The purpose of this server is to discuss academic topics. Do not provide bad faith responses to questions or requests. Additionally, if you don't have anything useful to say, don't say it.",
    "mentioning": "You must include your question in the mention and only use it once per question (e.g. use ?mention directly after you ask your question). Include specific questions, not vague or unanswerable ones. Use the proper role(s) that pertain to your question.",
    "spamming": "Do not send repeating messages, messages in quick succession, or reactions to a message needlessly. If a help mention (ping) is used, do not send messages unless it meaningfully contributes to the channel. Post your question in only one channel."}  # Dictionary with the server rules of HWH

class Rules(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @commands.slash_command(
        name="respect", description="Rule A) is displayed."
    )
    async def attempt(self, ctx: commands.Context) -> None:
        embed = EmbedBuilder(
            title="Please conduct yourself respectfully.",
            description=rules["respect"],
        ).build()
        await ctx.respond(embed=embed)
        
        @commands.slash_command(
            name="staff-reporting", description="Rule B) is displayed."
        )
        async def attempt(self, ctx: commands.Context) -> None:
            embed = EmbedBuilder(
                title="Please use staff report to notify us about rule violations only.",
                description=rules["staff-reporting"],
        ).build()
        await ctx.respond(embed=embed)
        
        @commands.slash_command(
            name="backseat-moderating", description="Rule C) is displayed."
        )
        async def attempt(self, ctx: commands.Context) -> None:
            embed = EmbedBuilder(
                title="Please refrain from backseat-moderating.",
                description=rules["backseat-moderating"],
        ).build()
        await ctx.respond(embed=embed)
            
        @commands.slash_command(
            name="underage", description="Rule D) is displayed."
        )
        async def attempt(self, ctx: commands.Context) -> None:
            embed = EmbedBuilder(
                title="The minimum age is 13 years.",
                description=rules["underage"],
        ).build()
        await ctx.respond(embed=embed)
        
        @commands.slash_command(
            name="unsolicited-dm", description="Rule E) is displayed."
        )
        async def attempt(self, ctx: commands.Context) -> None:
            embed = EmbedBuilder(
                title="Please don't send DMs without consent.",
                description=rules["unsolicited-dm"],
        ).build()
        await ctx.respond(embed=embed)
        
        @commands.slash_command(
            name="paywalls", description="Rule F) is displayed."
        )
        async def attempt(self, ctx: commands.Context) -> None:
            embed = EmbedBuilder(
                title="Trying to circumvent paywalls is not allowed.",
                description=rules["paywalls"],
        ).build()
        await ctx.respond(embed=embed)
        
        @commands.slash_command(
            name="clean-content", description="Rule G) is displayed."
        )
        async def attempt(self, ctx: commands.Context) -> None:
            embed = EmbedBuilder(
                title="Please keep content appropriate.",
                description=rules["clean-content"],
        ).build()
        await ctx.respond(embed=embed)
        
        @commands.slash_command(
            name="english-only", description="Rule H) is displayed."
        )
        async def attempt(self, ctx: commands.Context) -> None:
            embed = EmbedBuilder(
                title= "Please stick to English outside the language channels.",
                description=rules["english-only"],
        ).build()
        await ctx.respond(embed=embed)
        
        @commands.slash_command(
            name="advertising", description="Rule I) is displayed."
        )
        async def attempt(self, ctx: commands.Context) -> None:
            embed = EmbedBuilder(
                title="",
                description=rules["advertising"],
        ).build()
        await ctx.respond(embed=embed)
        
        @commands.slash_command(
            name="academic-integrity", description="Rule J) is displayed."
        )
        async def attempt(self, ctx: commands.Context) -> None:
            embed = EmbedBuilder(
                title="",
                description=rules["academic-integrity"],
        ).build()
        await ctx.respond(embed=embed)
        
        @commands.slash_command(
            name="bad-faith", description="Rule K) is displayed."
        )
        async def attempt(self, ctx: commands.Context) -> None:
            embed = EmbedBuilder(
                title="",
                description=rules["bad-faith"],
        ).build()
        await ctx.respond(embed=embed)
        
        @commands.slash_command(
            name="mentioning", description="Rule L) is displayed."
        )
        async def attempt(self, ctx: commands.Context) -> None:
            embed = EmbedBuilder(
                title="",
                description=rules["mentioning"],
        ).build()
        await ctx.respond(embed=embed)
        
        @commands.slash_command(
            name="spamming", description="Rule M) is displayed."
        )
        async def attempt(self, ctx: commands.Context) -> None:
            embed = EmbedBuilder(
                title="",
                description=rules["spamming"],
        ).build()
        await ctx.respond(embed=embed)
        
def setup(bot: commands.Bot) -> None:
    bot.add_cog(Information(bot))