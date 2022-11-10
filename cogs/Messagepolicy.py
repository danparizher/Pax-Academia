"""Scan messages in all applicable channels for duplicates and display a warning accordingly."""
#import re
import hashlib  # Used for hashing images
import discord
import time
from discord.commands import option
from discord.ext import commands

from util.EmbedBuilder import EmbedBuilder
from util.Logging import log

keeptime = 60000  # The time to keep sent messages before they are deleted in ms
recent_msgs = []  # All messages sent in the server within the last <keeptime> seconds
user_stats = {}  # The uIDs of all users who were found to be spamming or multiposting


class Messagepolicy(commands.Cog):
    """Check messages for multiposts or reposts in the same channel."""
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    # Allows the user to set the keeptime to a value other than the default
    @commands.slash_command(
        name="set-keeptime", description="Set the time to keep messages in the cache to check for duplicates."
    )
    @option(
        name="keeptime",
        description="The keeptime in milliseconds.",
        #autocomplete=get_keywords,
    )
    async def add_alert(self, ctx: commands.Context, keyword: str) -> None:
        """
        Allow a user to set the keeptime for messages in the cache.

        Parameters
        ----------
        ctx : commands.Context
            DESCRIPTION.
        keyword : str
            The keeptime in ms in string representation. Must be greater 0.

        Returns
        -------
        None
            DESCRIPTION.

        """
        old_keeptime = keeptime
        try:
            keeptime = int(keyword)
        except:
            embed = EmbedBuilder(
                title="Error",
                description="Please enter an integer number > 0.",
            ).build()
            await ctx.respond(embed=embed, ephemeral=True)
            return
            
        embed = EmbedBuilder(
            title="Success",
            description=f"Keeptime changed from {old_keeptime} to {keeptime}.",
        ).build()
        await ctx.respond(embed=embed, ephemeral=True)

        log(f"Keeptime changed by {ctx.author} in {ctx.guild} from {old_keeptime}  to {keeptime}.")

    # # Allows the user to remove an alert for a keyword.
    # @commands.slash_command(
    #     name="remove-alert",
    #     description="Removes an alert for a keyword.",
    # )
    # @option(
    #     name="keyword",
    #     description="The keyword to remove.",
    #     #autocomplete=get_keywords,
    # )
    # async def remove_alert(
    #     self,
    #     ctx: commands.Context,
    #     keyword: str,
    # ) -> None:

    #     # Check if the keyword is in the database.
    #     c = self.db.cursor()
    #     c.execute(
    #         "SELECT * FROM alerts WHERE keyword = ? AND user_id = ?",
    #         (keyword, ctx.author.id),
    #     )
    #     if not c.fetchone():
    #         embed = EmbedBuilder(
    #             title="Error",
    #             description="This keyword is not in the database.",
    #         ).build()
    #         await ctx.respond(embed=embed, ephemeral=True)
    #         return

    #     # Remove the keyword from the database.
    #     c.execute(
    #         "DELETE FROM alerts WHERE keyword = ? AND user_id = ?",
    #         (keyword, ctx.author.id),
    #     )
    #     self.db.commit()

    #     embed = EmbedBuilder(
    #         title="Success",
    #         description=f"Removed alert for keyword `{keyword}`.",
    #     ).build()
    #     await ctx.respond(embed=embed, ephemeral=True)

    #     log(f"Alert removed by {ctx.author} in {ctx.guild}.")

    # @commands.slash_command(name="list-alerts", description="Lists all alerts.")
    # async def list_alerts(self, ctx: commands.Context) -> None:
    #     # Get all alerts from the database.
    #     c = self.db.cursor()
    #     c.execute("SELECT * FROM alerts WHERE user_id = ?", (ctx.author.id,))
    #     alerts = c.fetchall()

    #     # Create a list of all alerts.
    #     alert_list = ""
    #     for alert in alerts:
    #         alert_list += f"`{alert[0]}`\n"

    #     # respond the list of alerts.
    #     embed = EmbedBuilder(
    #         title="Alerts",
    #         description=alert_list,
    #     ).build()
    #     await ctx.respond(embed=embed, ephemeral=True)

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message) -> None:
        """Check for multiposts upon a new user message."""
        async def user_posts() -> None:
            # Cases in which the bot does not cache the message
            if (
                message.author.bot
                or message.channel not in message.author.guild.channels
                or not message.author.guild.get_member(self.bot.user.id)
            ):
                print("No message caching!")
                return
            # Else the bot cachese the message
            else:
                print("Message caching activated!")
                files = [f.to_file() for f in message.attachments]  # Extract attachments from a message
                shasums = []  # SHA-sums of the attachments of the message if applicable
                for file in files:
                    h = hashlib.sha512()
                    while buf := file.read(h.block_size*1000):  # 128kB appear to be the sweetspot
                        h.update(buf)
                    shasums.append(h.hexdigest())
                
                content = message.content.lower()  # The text body of the message
                entry = [content, shasums, message.author.id, message.channel.id, time.time(), message.id]
                print("Cache entry:", entry)
                multipost_cnt = 0
                spam_cnt = 0
                
                for entry in recent_msgs:
                    print("Checking for duplicates in logs.")
                    # Check for duplicates in texts
                    if content in entry[0]:
                        print("Found a duplicate text message.")
                        if message.channel.id == entry[3]:
                            spam_cnt += 1
                        else:
                            multipost_cnt += 1
                    # Check for duplicates in attachments
                    for hashsum in entry[1]:
                        print("Found a duplicate attachment.")
                        if hashsum in shasums:
                            if message.channel.id == entry[3]:
                                spam_cnt += 1
                            else:
                                multipost_cnt += 1
                
                if multipost_cnt > 0 or spam_cnt > 0:
                    if message.user.id in user_stats.keys():  # Update the data base entry for the user if it already exists
                        user_stats[message.user.id][0] = user_stats[message.user.id][0] + spam_cnt
                        user_stats[message.user.id][1] = user_stats[message.user.id][1] + multipost_cnt
                        user_stats[message.user.id][2] = time.time()
                        log(f"User {message.author.mention} multiposted in {message.channel.mention}.")
                    else:  # Create a new entry if the user isn't in the data base already
                        user_stats[message.user.id] = [spam_cnt, multipost_cnt, time.time()]
                        log(f"User {message.author.mention} multiposted in {message.channel.mention}.")
                
                recent_msgs.append(entry)  # Save the message to the cache list
                
                # Omit old entries
                for entry in recent_msgs:
                    # The oldest message is always at index 0
                    if (time.time() - entry[4]) >= keeptime:
                        recent_msgs.pop(0)
                        
                for entry in user_stats:
                    # The oldest message is always at index 0
                    if (time.time() - entry[2]) >= keeptime:
                        user_stats.pop(0)
                
                
                

    #     async def tutor_alerts(self, message: discord.Message) -> None:
    #         if (
    #             message.author.id == self.bot.user.id
    #             or message.guild.id != 238956364729155585
    #         ):
    #             return

    #         keywords = [
    #             "dm me",
    #             "pay(ment)?",
    #             "paypal",
    #             "cashapp",
    #             "cash app",
    #             "venmo",
    #             "dollar(s)?",
    #             "tutor",
    #             "money",
    #             "price",
    #             "$",
    #             "professional",
    #         ]
    #         tutor_logs = self.bot.get_channel(1038985540147626024)
    #         # fmt: off
    #         if any(temp := sorted((lambda y: [x.group(0) for x in y if x != ""])([re.search(keyword, message.content, re.IGNORECASE) or "" for keyword in keywords]), key=lambda x: len(x), reverse=True,)):
    #         # fmt: on
    #             embed = EmbedBuilder(
    #                 title="Alert",
    #                 description=f"{message.author.mention} mentioned `{temp[0]}` in {message.channel.mention}.",
    #                 fields=[
    #                     ("Message", message.content, False),
    #                     (
    #                         "Message Link",
    #                         f"[Click to see message]({message.jump_url})",
    #                         False,
    #                     ),
    #                 ],
    #             ).build()
    #             await tutor_logs.send(embed=embed)

    #     await user_alerts()
    #     await tutor_alerts(self, message)

    # # @commands.slash_command(name="view-db", description="View the database.")
    # # async def view_db(self, ctx: commands.Context) -> None:
    # #     await ctx.respond(
    # #         content="Alerts Database",
    # #         file=discord.File("util/alerts.db"),
    # #         ephemeral=True,
    # #     )


def setup(bot) -> None:
    """Add the cog to the bot."""
    bot.add_cog(Messagepolicy(bot))
