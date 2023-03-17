import discord


class EmbedBuilder:
    def __init__(
        self,
        title: str | None = None,
        description: str | None = None,
        color: int = 0xFF7900,
        image: str | None = None,
        fields: list | None = None,
        thumbnail: str | None = None,
        url: str | None = None,
    ) -> None:
        self.title = title
        self.description = description
        self.color = color
        self.thumbnail = thumbnail
        self.footer = "Powered by Homework Help"
        self.icon_url = "https://pbs.twimg.com/profile_images/988662835180797952/9fWyq5hr_400x400.jpg"
        self.image = image
        self.fields = fields
        self.url = url

    def build(self) -> discord.Embed:
        embed = discord.Embed(
            title=self.title,
            description=self.description,
            color=self.color,
        )
        if self.image:
            embed.set_image(url=self.image)
        if self.thumbnail:
            embed.set_thumbnail(url=self.thumbnail)
        if self.fields:
            for field in self.fields:
                embed.add_field(name=field[0], value=field[1], inline=field[2])
        if self.url:
            embed.url = self.url
        embed.set_footer(text=self.footer, icon_url=self.icon_url)
        return embed
