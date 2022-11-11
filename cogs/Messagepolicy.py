"""Scan messages in all applicable channels for duplicates and display a warning accordingly."""
#import re
import hashlib  # Used for hashing images
import discord
import time
from discord.commands import option
from discord.ext import commands

from util.EmbedBuilder import EmbedBuilder
from util.Logging import log


recent_msgs = []  # All messages sent in the server within the last <keeptime> seconds
user_stats = {}  # The uIDs of all users who were found to be spamming or multiposting


class Messagepolicy(commands.Cog):
    """Check messages for multiposts or reposts in the same channel."""
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.keeptime = 60  # The time to keep sent messages before they are deleted in seconds

    # Allows the user to set the keeptime to a value other than the default
    @commands.slash_command(
        name="set-keeptime", description="Set the time to keep messages in the cache to check for duplicates."
    )
    @option(
        name="keeptime",
        description="The keeptime in seconds.",
        #autocomplete=get_keywords,
    )
    async def change_keeptime(self, ctx: commands.Context, keyword: str) -> None:
        """
        Allow a user to set the keeptime for messages in the cache.

        Parameters
        ----------
        ctx : commands.Context
            DESCRIPTION.
        keyword : str
            The keeptime in seconds in string representation. Must be greater 0.

        Returns
        -------
        None
            DESCRIPTION.

        """
        old_keeptime = self.keeptime
        try:
            self.keeptime = int(keyword)
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
                if len(files) > 0:  # TODO: Check if this mitigates some errors which appeared with content hashing
                    for file in files:
                        h = hashlib.sha512()
                        while buf := file.read(h.block_size*1000):  # 128kB appear to be the sweetspot
                            h.update(buf)
                        shasums.append(h.hexdigest())
                
                content = message.content.lower()  # The text body of the message
                content = hashlib.sha512(content.encode())  # Hash the text of the message
                entry = [content, shasums, message.author.id, message.channel.id, time.time(), message.id]
                print("Cache entry:", entry)
                multipost_cnt = 0
                spam_cnt = 0
                
                for entry in recent_msgs:
                    print("Checking entry:", entry)
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
                    if (time.time() - entry[4]) >= self.keeptime:
                        recent_msgs.pop(0)
                        
                for entry in user_stats:
                    # The oldest message is always at index 0
                    if (time.time() - entry[2]) >= self.keeptime:
                        user_stats.pop(0)
        
        await user_posts()

def setup(bot) -> None:
    """Add the cog to the bot."""
    bot.add_cog(Messagepolicy(bot))
