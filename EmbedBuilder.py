import discord


class EmbedBuilder:
    def __init__(
        self,
        title,
        description,
        color=0xFF7900,
        image=None,
        fields=None,
        thumbnail=None,
    ) -> None:
        self.title: str | None = title
        self.description: str | None = description
        self.color: int = color
        self.thumbnail: str | None = thumbnail
        self.footer: str = "Powered by Homework Help"
        self.icon_url: str = "https://pbs.twimg.com/profile_images/988662835180797952/9fWyq5hr_400x400.jpg"
        self.image: str | None = image
        self.fields: list | None = fields

    def build(self) -> discord.Embed:
        embed = discord.Embed(
            title=self.title, description=self.description, color=self.color
        )
        if self.image:
            embed.set_image(url=self.image)
        if self.thumbnail:
            embed.set_thumbnail(url=self.thumbnail)
        if self.fields:
            for field in self.fields:
                embed.add_field(name=field[0], value=field[1], inline=field[2])
        embed.set_footer(text=self.footer, icon_url=self.icon_url)
        return embed
