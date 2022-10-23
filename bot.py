import os

import discord
from dotenv import load_dotenv

from webcache import main

load_dotenv()
TOKEN: str | None = os.getenv("DISCORD_TOKEN")

client = discord.Client()


@client.event
async def on_ready() -> None:
    print(f"{client.user} has connected to Discord!")


@client.event
async def on_message(message) -> None:
    if message.author == client.user:
        return

    if message.content.startswith("/fixgrammar"):
        await message.channel.send(main())


client.run(TOKEN)
