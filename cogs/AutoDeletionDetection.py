import discord
from discord.ext import commands


# detect if a user is deleting their own messages in quick succession
class AutoDeletionDetection(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @commands.Cog.listener()
    async def on_message_delete(self, message: discord.Message) -> None:
        """
        If a user deletes their own messages in quick succession, send a log to the channel.
        For example, if a user deletes 5 messages in 5 seconds, send a log to the channel.
        """
        # ignore messages from bots
        if message.author.bot:
            return

        # get the user's last 5 messages
        messages = await message.channel.history(
            limit=5,
            before=message,
            oldest_first=False,
        ).flatten()

        # if the user has less than 5 messages, return
        if len(messages) < 5:
            return

        # if the user is not the author of all 5 messages, return
        if any(m.author != message.author for m in messages):
            return

        # if the user deleted their last 5 messages in less than 5 seconds, send a log to the channel
        if (messages[0].created_at - messages[-1].created_at).total_seconds() <= 5:
            await message.channel.send(
                f"{message.author.mention} deleted their last 5 messages in less than 5 seconds.",
            )


def setup(bot: commands.Bot) -> None:
    bot.add_cog(AutoDeletionDetection(bot))
