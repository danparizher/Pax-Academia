import discord

# TODO: Incorporate HWH logo into embeds.


class EmbedBuilder:
    def __init__(self, title, description, color=0xFF7900, image=None) -> None:
        self.title: str | None = title
        self.description: str | None = description
        self.color: int = color
        self.footer: str = "Powered by Homework Help"
        self.image: str | None = image

    def build(self) -> discord.Embed:
        embed = discord.Embed(
            title=self.title, description=self.description, color=self.color
        )
        if self.image:
            embed.set_image(url=self.image)
        embed.set_footer(text=self.footer)
        return embed
