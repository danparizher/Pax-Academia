import discord


class EmbedBuilder:
    def __init__(
        self,
        title: str | None = None,
        description: str | None = None,
        color: int = 0xFF7900,
        image: str | None = None,
        fields: list[tuple[str, str, bool]] | None = None,
        thumbnail: str | None = None,
        footer: str = "Powered by Homework Help",
        icon_url: str = "https://pbs.twimg.com/profile_images/988662835180797952/9fWyq5hr_400x400.jpg",
        url: str | None = None,
    ) -> None:
        self.title = title
        self.description = description
        self.color = color
        self.thumbnail = thumbnail
        self.footer = footer
        self.icon_url = icon_url
        self.image = image
        self.fields = fields
        self.url = url

    def build(self) -> discord.Embed:
        embed = discord.Embed(
            title=self.title[:256] if self.title else None,
            description=self.description[:4096] if self.description else None,
            color=self.color,
        )

        if self.image:
            embed.set_image(url=self.image)
        if self.thumbnail:
            embed.set_thumbnail(url=self.thumbnail)
        if self.fields:
            for name, value, inline in self.fields:
                embed.add_field(name=name[:256], value=value[:1024], inline=inline)
        if self.url:
            embed.url = self.url
        embed.set_footer(text=self.footer[:2048], icon_url=self.icon_url)
        return embed
