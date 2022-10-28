import discord

# TODO: Incorporate HWH logo into embeds.


class EmbedBuilder:
    def __init__(
        self,
        title,
        description,
        color=0xFF7900,
        image=None,
        thumbnail="https://media-exp1.licdn.com/dms/image/C560BAQF9f_j13_jk9g/company-logo_200_200/0/1619494448942?e=1675296000&v=beta&t=LYn4OQyBazxw113Bna4GyHsL8QXyltt0uCQ5rE0IdGM",
    ) -> None:
        self.title: str | None = title
        self.description: str | None = description
        self.color: int = color
        self.thumbnail: str | None = thumbnail
        self.footer: str = "Powered by Homework Help"
        self.image: str | None = image

    def build(self) -> discord.Embed:
        embed = discord.Embed(
            title=self.title, description=self.description, color=self.color
        )
        if self.image:
            embed.set_image(url=self.image)
        if self.thumbnail:
            embed.set_thumbnail(url=self.thumbnail)
        embed.set_footer(text=self.footer)
        return embed
