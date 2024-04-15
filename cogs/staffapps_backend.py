# imports
from __future__ import annotations

from datetime import datetime
from os import getenv
from time import time

import discord
import discord.ui
from discord import option
from discord.ext import commands

import database
from message_formatting.embeds import EmbedBuilder
from util.limiter import limit
from util.logger import log


class staffAppsSeeAll(discord.ui.View):
    """
    A discord view for the staffAppsSeeAll command
    """

    def __init__(self, author: discord.Member | discord.User, data: list) -> None:
        super().__init__()
        self.author = author
        self.data = data
        self.cur_page = 1
        self.max_page = len(data) // 10 + 1

    async def repopulate(self, interaction: discord.Interaction) -> None:
        """
        Repopulates the view with the next page of data after a button press.
        """
        title = f"Applications page {self.cur_page}/{self.max_page}"
        field_title = "Application ID, Discord Name, Status, Submission Time"
        field_content = "".join(
            f"{row[0]}, {row[1]}, {row[2]}, {datetime.fromtimestamp(int(row[3]))}\n"
            for row in self.data[self.cur_page * 10 - 10 : self.cur_page * 10]
        )
        fields = [(field_title, field_content, False)]
        embed = EmbedBuilder(
            title=title,
            description="",
            fields=fields,
            color=0x24AAE1,
        )  # hwh blue
        await interaction.response.edit_message(embed=embed.build(), view=self)

    @property
    def back_button_child(self) -> discord.ui.Button:
        assert isinstance(self.children[0], discord.ui.Button)
        return self.children[0]

    @discord.ui.button(
        label="",
        style=discord.ButtonStyle.primary,
        emoji="⬅️",
        disabled=True,
    )
    async def back_button_callback(
        self,
        button: discord.ui.Button,
        interaction: discord.Interaction,
    ) -> None:
        self.forward_button_child.disabled = False
        self.cur_page -= 1
        if self.cur_page == 1:
            button.disabled = True
        await self.repopulate(interaction)

    @property
    def forward_button_child(self) -> discord.ui.Button:
        assert isinstance(self.children[1], discord.ui.Button)
        return self.children[1]

    @discord.ui.button(
        label="",
        style=discord.ButtonStyle.primary,
        emoji="➡️",
        disabled=False,
    )
    async def forward_button_callback(
        self,
        button: discord.ui.Button,
        interaction: discord.Interaction,
    ) -> None:
        self.back_button_child.disabled = False
        self.cur_page += 1
        if self.cur_page == self.max_page:
            button.disabled = True
        await self.repopulate(interaction)


class staffAppsSeeDeniedAccepted(discord.ui.View):
    """
    A discord view for the denied and accepted commands
    """

    def __init__(
        self,
        author: discord.Member | discord.User,
        data: list,
        da: str,
    ) -> None:
        super().__init__()
        self.author = author
        self.data = data
        self.cur_page = 1
        self.max_page = len(data) // 10 + 1
        self.da = da  # d for denied, a for accepted

    async def repopulate(self, interaction: discord.Interaction) -> None:
        """
        Repopulates the view with the next page of data after a button press.
        """
        title = f"{'Denied' if self.da == 'd' else 'Accepted'} Applications page {self.cur_page}/{self.max_page}"
        field_title = "Application ID, Discord Name, Original Submission Time"
        field_content = "".join(
            f"{row[0]}, {row[1]}, {datetime.fromtimestamp(int(row[2]))}\n"
            for row in self.data[self.cur_page * 10 - 10 : self.cur_page * 10]
        )
        fields = [(field_title, field_content, False)]
        embed = EmbedBuilder(
            title=title,
            description="",
            fields=fields,
            color=0x9D0006 if self.da == "d" else 0x80C545,
        )  # soft red or hwh green
        await interaction.response.edit_message(embed=embed.build(), view=self)

    @property
    def back_button_child(self) -> discord.ui.Button:
        assert isinstance(self.children[0], discord.ui.Button)
        return self.children[0]

    @discord.ui.button(
        label="",
        style=discord.ButtonStyle.primary,
        emoji="⬅️",
        disabled=True,
    )
    async def back_button_callback(
        self,
        button: discord.ui.Button,
        interaction: discord.Interaction,
    ) -> None:
        self.forward_button_child.disabled = False
        self.cur_page -= 1
        if self.cur_page == 1:
            button.disabled = True
        await self.repopulate(interaction)

    @property
    def forward_button_child(self) -> discord.ui.Button:
        assert isinstance(self.children[1], discord.ui.Button)
        return self.children[1]

    @discord.ui.button(
        label="",
        style=discord.ButtonStyle.primary,
        emoji="➡️",
        disabled=False,
    )
    async def forward_button_callback(
        self,
        button: discord.ui.Button,
        interaction: discord.Interaction,
    ) -> None:
        self.back_button_child.disabled = False
        self.cur_page += 1
        if self.cur_page == self.max_page:
            button.disabled = True
        await self.repopulate(interaction)


class staffAppsSeeSpam(discord.ui.View):
    def __init__(self, author: discord.Member | discord.User, data: list) -> None:
        """
        A discord view for the spam command
        """
        super().__init__()
        self.author = author
        self.data = data
        self.cur_page = 1
        self.max_page = len(data)

    async def repopulate(self, interaction: discord.Interaction) -> None:
        self.db = database.connect()
        self.cursor = self.db.cursor()
        first_user_data = self.cursor.execute(
            "select * from application where uid = ?",
            (self.data[self.cur_page - 1][0],),
        ).fetchall()
        self.db.close()
        count = len(first_user_data)
        name = first_user_data[0][3]
        most_recent = datetime.fromtimestamp(
            max(int(data[10]) for data in first_user_data),
        )

        title = f"Banned users / Marked as spam page {self.cur_page}/{len(self.data)}"
        field_content = f"Application count: **{count}**\nMost recent application: **{most_recent}**\n"
        fields = [(name, field_content, False)]
        embed = EmbedBuilder(
            title=title,
            description="",
            fields=fields,
            color=0xDD4C35,
        )  # red
        await interaction.response.edit_message(embed=embed.build(), view=self)

    @property
    def back_button_child(self) -> discord.ui.Button:
        assert isinstance(self.children[0], discord.ui.Button)
        return self.children[0]

    @discord.ui.button(
        label="",
        style=discord.ButtonStyle.primary,
        emoji="⬅️",
        disabled=True,
    )
    async def back_button_callback(
        self,
        button: discord.ui.Button,
        interaction: discord.Interaction,
    ) -> None:
        self.forward_button_child.disabled = False
        self.cur_page -= 1
        if self.cur_page == 1:
            button.disabled = True
        await self.repopulate(interaction)

    @property
    def forward_button_child(self) -> discord.ui.Button:
        assert isinstance(self.children[1], discord.ui.Button)
        return self.children[1]

    @discord.ui.button(
        label="",
        style=discord.ButtonStyle.primary,
        emoji="➡️",
        disabled=False,
    )
    async def forward_button_callback(
        self,
        button: discord.ui.Button,
        interaction: discord.Interaction,
    ) -> None:
        self.back_button_child.disabled = False
        self.cur_page += 1
        if self.cur_page == self.max_page:
            button.disabled = True
        await self.repopulate(interaction)

    @property
    def unban_button_child(self) -> discord.ui.Button:
        assert isinstance(self.children[2], discord.ui.Button)
        return self.children[2]

    @discord.ui.button(
        label="Unban",
        style=discord.ButtonStyle.danger,
        emoji="❗",
        row=1,
    )
    async def unban_button_callback(
        self,
        button: discord.ui.Button,
        interaction: discord.Interaction,
    ) -> None:
        self.db = database.connect()
        self.cursor = self.db.cursor()
        self.cursor.execute(
            "update user set markedSpam = 0 where uid = ?",
            (self.data[self.cur_page - 1][0],),
        )
        self.db.commit()
        self.db.close()
        embed = EmbedBuilder(
            title="User unbanned.",
            description="This user can now apply for staff again.",
            color=0x80C545,
        )  # hwh green
        await interaction.response.edit_message(
            content="",
            embed=embed.build(),
            view=None,
        )
        log(
            f"$ unbanned user {self.data[self.cur_page - 1][0]} from applying for staff.",
            self.author,
        )


class staffAppsSeeSpamSimple(discord.ui.View):
    def __init__(self, author: int) -> None:
        super().__init__()
        self.author = author

    @property
    def unban_button_child(self) -> discord.ui.Button:
        assert isinstance(self.children[0], discord.ui.Button)
        return self.children[0]

    @discord.ui.button(
        label="Unban",
        style=discord.ButtonStyle.danger,
        emoji="❗",
        row=1,
    )
    async def unban_button_callback(
        self,
        button: discord.ui.Button,
        interaction: discord.Interaction,
    ) -> None:
        self.db = database.connect()
        self.cursor = self.db.cursor()
        self.cursor.execute(
            "update user set markedSpam = 0 where uid = ?",
            (self.author,),
        )
        self.db.commit()
        self.db.close()
        log(f"$ unbanned user {self.author} from applying for staff.", interaction.user)
        embed = EmbedBuilder(
            title="User unbanned.",
            description="This user can now apply for staff again.",
            color=0x80C545,
        )  # hwh green
        await interaction.response.edit_message(
            content="",
            embed=embed.build(),
            view=None,
        )


class staffAppsMain(discord.ui.View):
    def __init__(self, author: discord.Member | discord.User, data: list) -> None:
        """
        The main view for the staff applications command
        """
        super().__init__()
        self.author = author
        self.data = data
        self.cur_page = 0
        self.max_page = len(data)
        self.colors = {
            1: 0xFFFFFF,
            2: 0xFF0000,
            3: 0xFF00FF,
            4: 0x9900FF,
            5: 0xFFFF00,
            6: 0xFFC000,
            7: 0xA4C2F4,
            8: 0x00FF00,
            9: 0x38761D,
        }  # colours taken from @czar's infographic

    async def repopulate(self, interaction: discord.Interaction) -> None:
        """
        Repopulates the view with the next page of data, enables and disables buttons as needed
        """
        self.spam_button_child.disabled = False
        self.deny_button_child.disabled = False
        self.advance_button_child.disabled = False
        if self.cur_page != 1:
            self.back_button_child.disabled = False
        if self.data[self.cur_page - 1][2] == 1:
            self.second_opinion_button_child.disabled = False
        else:
            self.second_opinion_button_child.disabled = True

        # long application check
        if (
            len(self.data[self.cur_page - 1][8]) > 1024
            or len(self.data[self.cur_page - 1][9]) > 1024
        ):
            self.edit_button_child.disabled = False
        else:
            self.edit_button_child.disabled = True

        self.db = database.connect()
        self.cursor = self.db.cursor()
        statusname = self.cursor.execute(
            "select s.description from application a join status s on a.status = s.statusID where appId = ?;",
            (self.data[self.cur_page - 1][0],),
        ).fetchone()[0]
        status_int = self.data[self.cur_page - 1][2]
        # check likes and dislikes and disable buttons if necessary
        like_amount = len(
            self.cursor.execute(
                "select likes from like where uid = ? and appId = ?;",
                (self.author.id, self.data[self.cur_page - 1][0]),
            ).fetchall(),
        )
        like_list = [
            x[0]
            for x in self.cursor.execute(
                "select likes from like where appId = ?;",
                (self.data[self.cur_page - 1][0],),
            ).fetchall()
        ]
        likes = like_list.count(1)
        dislikes = like_list.count(0)
        if like_amount > 0:
            self.like_button_child.disabled = True
            self.dislike_button_child.disabled = True
        else:
            self.like_button_child.disabled = False
            self.dislike_button_child.disabled = False
        self.db.close()
        title = f"Staff applications page {self.cur_page}/{len(self.data)}"
        description = f"Application ID: **{self.data[self.cur_page - 1][0]}**\nApplicant Name: **{self.data[self.cur_page - 1][3]}**\nApplicant ID: **{self.data[self.cur_page - 1][1]}**\n"
        fields = [
            ("Status", statusname, False),
            ("First Name", self.data[self.cur_page - 1][4], False),
            ("Time Zone", self.data[self.cur_page - 1][6], False),
            ("Hours available per Week", self.data[self.cur_page - 1][7], False),
            (
                "Why do you want to become a staff member?",
                self.data[self.cur_page - 1][8][:1024],
                False,
            ),
            (
                "How will you contribute if you become a staff member?",
                self.data[self.cur_page - 1][9][:1024],
                False,
            ),
            (
                "Submission Time",
                str(datetime.fromtimestamp(int(self.data[self.cur_page - 1][10]))),
                False,
            ),
            ("Likes / dislikes", f"👍 {likes} / {dislikes} 👎", False),
        ]
        embed = EmbedBuilder(
            title=title,
            description=description,
            fields=fields,
            color=self.colors[status_int],
        )  # hwh green
        await interaction.response.edit_message(embed=embed.build(), view=self)

    @property
    def back_button_child(self) -> discord.ui.Button:
        assert isinstance(self.children[0], discord.ui.Button)
        return self.children[0]

    @discord.ui.button(
        label="",
        style=discord.ButtonStyle.primary,
        emoji="⬅️",
        disabled=True,
    )
    async def back_button_callback(
        self,
        button: discord.ui.Button,
        interaction: discord.Interaction,
    ) -> None:
        self.forward_button_child.disabled = False
        self.cur_page -= 1
        if self.cur_page == 1:
            button.disabled = True
        await self.repopulate(interaction)

    @property
    def forward_button_child(self) -> discord.ui.Button:
        assert isinstance(self.children[1], discord.ui.Button)
        return self.children[1]

    @discord.ui.button(
        label="",
        style=discord.ButtonStyle.primary,
        emoji="➡️",
        disabled=False,
    )
    async def forward_button_callback(
        self,
        button: discord.ui.Button,
        interaction: discord.Interaction,
    ) -> None:
        self.back_button_child.disabled = False
        self.cur_page += 1
        if self.cur_page == self.max_page:
            button.disabled = True
        await self.repopulate(interaction)

    @property
    def spam_button_child(self) -> discord.ui.Button:
        assert isinstance(self.children[2], discord.ui.Button)
        return self.children[2]

    @discord.ui.button(
        label="Mark as spam",
        style=discord.ButtonStyle.danger,
        emoji="❌",
        disabled=True,
        row=1,
    )
    async def spam_button_callback(
        self,
        button: discord.ui.Button,
        interaction: discord.Interaction,
    ) -> None:
        self.db = database.connect()
        self.cursor = self.db.cursor()
        self.cursor.execute(
            "update user set markedSpam = 1 where uid = ?",
            (self.data[self.cur_page - 1][1],),
        )
        self.cursor.execute(
            "update application set status = 2 where appId = ?",
            (self.data[self.cur_page - 1][0],),
        )
        self.db.commit()
        self.db.close()
        log(f"User {self.data[self.cur_page - 1][1]} marked as spam by $", self.author)
        embed = EmbedBuilder(
            title="User marked as spam.",
            description="This user can no longer apply for staff.",
            color=0xF8312F,
        )  # red
        await interaction.response.edit_message(
            content="",
            embed=embed.build(),
            view=None,
        )

    @property
    def deny_button_child(self) -> discord.ui.Button:
        assert isinstance(self.children[3], discord.ui.Button)
        return self.children[3]

    @discord.ui.button(
        label="Deny",
        style=discord.ButtonStyle.danger,
        emoji="❗",
        disabled=True,
        row=1,
    )
    async def deny_button_callback(
        self,
        button: discord.ui.Button,
        interaction: discord.Interaction,
    ) -> None:
        self.db = database.connect()
        self.cursor = self.db.cursor()
        self.cursor.execute(
            "update application set status = 2 where appId = ?",
            (self.data[self.cur_page - 1][0],),
        )
        cooldown = int(time()) + 2678400  # 31 days
        self.cursor.execute(
            "update user set cooldown = ? where uid = ?",
            (cooldown, self.data[self.cur_page - 1][1]),
        )
        self.db.commit()
        self.db.close()
        log(f"Application {self.data[self.cur_page - 1][0]} denied by $", self.author)
        embed = EmbedBuilder(
            title="Application denied.",
            description="This application has been denied and a cooldown has been applied.",
            color=0xF8312F,
        )  # red
        await interaction.response.edit_message(
            content="",
            embed=embed.build(),
            view=None,
        )

    @property
    def advance_button_child(self) -> discord.ui.Button:
        assert isinstance(self.children[4], discord.ui.Button)
        return self.children[4]

    @discord.ui.button(
        label="Advance to next stage",
        style=discord.ButtonStyle.success,
        emoji="✅",
        disabled=True,
        row=2,
    )
    async def advance_button_callback(
        self,
        button: discord.ui.Button,
        interaction: discord.Interaction,
    ) -> None:
        self.db = database.connect()
        self.cursor = self.db.cursor()
        current_status = self.data[self.cur_page - 1][2]
        if current_status == 1:
            status_name = [
                x[0]
                for x in self.cursor.execute(
                    "select description from status where statusId in (?, ?)",
                    (current_status, current_status + 3),
                ).fetchall()
            ]
            self.cursor.execute(
                "update application set status = 4 where appId = ?",
                (self.data[self.cur_page - 1][0],),
            )
        else:
            status_name = [
                x[0]
                for x in self.cursor.execute(
                    "select description from status where statusId in (?, ?)",
                    (current_status, current_status + 1),
                ).fetchall()
            ]
            self.cursor.execute(
                "update application set status = ? where appId = ?",
                (current_status + 1, self.data[self.cur_page - 1][0]),
            )
        title = "Application status updated."
        description = f"Application ID: **{self.data[self.cur_page - 1][0]}**\nApplicant name: **{self.data[self.cur_page - 1][3]}**\nApplicant ID: **{self.data[self.cur_page - 1][1]}**\n \
            Status changed from **{status_name[0]}** -> **{status_name[1]}**."
        self.db.commit()
        self.db.close()
        log(
            f"Application {self.data[self.cur_page - 1][0]} status changed from {status_name[0]} -> {status_name[1]} by $",
            self.author,
        )
        embed = EmbedBuilder(
            title=title,
            description=description,
            color=0x00FF00,
        )  # green
        await interaction.response.edit_message(
            content="",
            embed=embed.build(),
            view=None,
        )

    @property
    def second_opinion_button_child(self) -> discord.ui.Button:
        assert isinstance(self.children[5], discord.ui.Button)
        return self.children[5]

    @discord.ui.button(
        label="",
        style=discord.ButtonStyle.secondary,
        emoji="2️⃣",
        disabled=True,
        row=2,
    )
    async def second_opinion_button_callback(
        self,
        button: discord.ui.Button,
        interaction: discord.Interaction,
    ) -> None:
        self.db = database.connect()
        self.cursor = self.db.cursor()
        self.cursor.execute(
            "update application set status = 3 where appId = ?",
            (self.data[self.cur_page - 1][0],),
        )
        title = "Application status updated."
        description = f"Application ID: **{self.data[self.cur_page - 1][0]}**\nApplicant name: **{self.data[self.cur_page - 1][3]}**\nApplicant ID: **{self.data[self.cur_page - 1][1]}**\n \
            Status changed from **Application submitted** -> **Second Opinion required**."
        self.db.commit()
        self.db.close()
        log(
            f"Application {self.data[self.cur_page - 1][0]} status changed from Application submitted -> Second Opinion required by $",
            self.author,
        )
        embed = EmbedBuilder(
            title=title,
            description=description,
            color=0x00FF00,
        )  # green
        await interaction.response.edit_message(
            content="",
            embed=embed.build(),
            view=None,
        )

    @property
    def like_button_child(self) -> discord.ui.Button:
        assert isinstance(self.children[6], discord.ui.Button)
        return self.children[6]

    @discord.ui.button(
        label="",
        style=discord.ButtonStyle.secondary,
        emoji="👍",
        disabled=True,
        row=3,
    )
    async def like_button_callback(
        self,
        button: discord.ui.Button,
        interaction: discord.Interaction,
    ) -> None:
        assert (
            interaction.user is not None
        ), "Our Discord server must be haunted! Every interaction must be paired with a user."

        self.db = database.connect()
        self.cursor = self.db.cursor()
        self.cursor.execute(
            "insert into like (appId, uid, name, likes) values (?, ?, ?, ?)",
            (
                self.data[self.cur_page - 1][0],
                interaction.user.id,
                f"@{interaction.user.name}"
                if str(interaction.user.discriminator) == "0"
                else f"{interaction.user.name}#{interaction.user.discriminator}",
                1,
            ),
        )
        self.db.commit()
        self.db.close()
        log(
            f"Application {self.data[self.cur_page - 1][0]} liked by $ ({interaction.user.id})",
            interaction.user,
        )
        embed = EmbedBuilder(
            title="Like added.",
            description="You have liked this application.",
            color=0x00FF00,
        )  # green
        await interaction.response.edit_message(
            content="",
            embed=embed.build(),
            view=None,
        )

    @property
    def dislike_button_child(self) -> discord.ui.Button:
        assert isinstance(self.children[7], discord.ui.Button)
        return self.children[7]

    @discord.ui.button(
        label="",
        style=discord.ButtonStyle.secondary,
        emoji="👎",
        disabled=True,
        row=3,
    )
    async def dislike_button_callback(
        self,
        button: discord.ui.Button,
        interaction: discord.Interaction,
    ) -> None:
        assert (
            interaction.user is not None
        ), "Our Discord server must be haunted! Every interaction must be paired with a user."

        self.db = database.connect()
        self.cursor = self.db.cursor()
        self.cursor.execute(
            "insert into like (appId, uid, name, likes) values (?, ?, ?, ?)",
            (
                self.data[self.cur_page - 1][0],
                interaction.user.id,
                f"@{interaction.user.name}"
                if str(interaction.user.discriminator) == "0"
                else f"{interaction.user.name}#{interaction.user.discriminator}",
                0,
            ),
        )
        self.db.commit()
        self.db.close()
        log(
            f"Application {self.data[self.cur_page - 1][0]} disliked by $ ({interaction.user.id})",
            interaction.user,
        )
        embed = EmbedBuilder(
            title="Dislike added.",
            description="You have liked this application.",
            color=0xF8312F,
        )  # red
        await interaction.response.edit_message(
            content="",
            embed=embed.build(),
            view=None,
        )

    @property
    def edit_button_child(self) -> discord.ui.Button:
        assert isinstance(self.children[8], discord.ui.Button)
        return self.children[8]

    @discord.ui.button(
        label="",
        style=discord.ButtonStyle.secondary,
        emoji="📝",
        disabled=True,
        row=3,
    )
    async def edit_button_callback(
        self,
        button: discord.ui.Button,
        interaction: discord.Interaction,
    ) -> None:
        why_reason = self.data[self.cur_page - 1][8]
        contribute_reason = self.data[self.cur_page - 1][9]
        embed1 = EmbedBuilder(
            title="Why do you want to join?",
            description=why_reason,
            color=0x00FF00,
        )  # green
        embed2 = EmbedBuilder(
            title="What can you contribute to the server?",
            description=contribute_reason,
            color=0x00FF00,
        )  # green

        await interaction.response.send_message(
            embed=embed1.build(),
            ephemeral=True,
            view=fullViewApplication(embed1, embed2),
        )


class fullViewApplication(discord.ui.View):
    def __init__(self, embed1: EmbedBuilder, embed2: EmbedBuilder) -> None:
        super().__init__()
        self.embeds = [embed1, embed2]
        self.cur_state = 0

    @discord.ui.button(
        label="",
        style=discord.ButtonStyle.secondary,
        emoji="🔄",
        disabled=False,
        row=0,
    )
    async def button0_callback(
        self,
        button: discord.ui.Button,
        interaction: discord.Interaction,
    ) -> None:
        self.cur_state = not self.cur_state
        await interaction.response.edit_message(
            embed=self.embeds[self.cur_state].build(),
            view=self,
        )


SEE_GUILD = getenv("ALLOW_VIEW_DATABASE_GUILD_ID")
SEE_ROLE = getenv("ALLOW_SEE_APPS_ROLE")
SEE_PERMISSIONS = (lambda x: x) if SEE_ROLE is None else commands.has_role(SEE_ROLE)
SUBCOMMANDS = ["all", "spam", "accepted", "denied"]


class StaffAppsBackoffice(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.db = database.connect()
        self.cursor = self.db.cursor()

    @SEE_PERMISSIONS
    @commands.slash_command(
        name="see-apps",
        description="Command to check and work with applications.",
        guild_ids=None if SEE_GUILD is None else [SEE_GUILD],
        guild_only=SEE_GUILD is not None,
    )
    @option(
        "subcommand",
        str,
        description="The subcommand to use. (may be empty)",
        required=False,
        choices=SUBCOMMANDS,
    )
    @option(
        "specific_id",
        int,
        description="The specific application ID to check. IGNORES SUBCOMMAND",
        required=False,
    )
    @limit(1)
    async def see_apps(
        self,
        ctx: discord.ApplicationContext,
        subcommand: str,
        specific_id: int,
    ) -> None:
        if str(ctx.author.discriminator) == "0":
            username = f"@{ctx.author.name}"
        else:
            username = f"{ctx.author.name}#{ctx.author.discriminator}"
        log(f"see-apps command used by {username}:({ctx.author.id})")
        if specific_id:
            data = self.cursor.execute(
                "select a.appId, a.uid, a.discordName, a.firstName, a.timezone, a.hoursAvailableWk, a.staffReason, a.contributeReason, a.submissionTime, s.description from application a join status s on a.status = s.statusId where appId = ?;",
                (specific_id,),
            ).fetchone()
            if not data:
                await ctx.respond("Application not found.", ephemeral=True)
                return
            like_list = [
                x[0]
                for x in self.cursor.execute(
                    "select likes from like where appId = ?;",
                    (specific_id,),
                ).fetchall()
            ]
            likes = like_list.count(1)
            dislikes = like_list.count(0)
            title = "Staff application"
            description = f"Application ID: **{data[0]}**\nApplicant name: **{data[2]}**\nApplicant ID: **{data[1]}**\n"
            fields = [
                ("Status", data[9], False),
                ("first name", data[3], False),
                ("Time Zone", data[4], False),
                ("Hours available per Week", data[5], False),
                ("Why do you want to become a staff member?", data[6][:1024], False),
                (
                    "How will you contribute if you become a staff member?",
                    data[7][:1024],
                    False,
                ),
                ("Submission Time", str(datetime.fromtimestamp(int(data[8]))), False),
                ("Likes / dislikes", f"👍 {likes} / {dislikes} 👎", False),
            ]
            embed = EmbedBuilder(
                title=title,
                description=description,
                fields=fields,
                color=0x30FFF1,
            )  # hwh green
            await ctx.respond(embed=embed.build(), ephemeral=True)
            log(f"{username} viewed a specific application: {specific_id}")
            return

        if subcommand == "all":
            # gather first page of applications
            data = self.cursor.execute(
                "select appId, discordName, description, submissionTime from application a join status s on a.status = s.statusId order by appId ASC",
            ).fetchall()
            title = f"Applications page 1/{len(data) // 10 + 1}"
            field_title = "Application ID, Discord Name, Status, Submission Time"
            field_content = "".join(
                f"{row[0]}, {row[1]}, {row[2]}, {datetime.fromtimestamp(int(row[3]))}\n"
                for row in data[:10]
            )
            fields = [(field_title, field_content, False)]
            embed = EmbedBuilder(
                title=title,
                description="",
                fields=fields,
                color=0x24AAE1,
            )  # hwh blue
            if len(data) > 10:
                await ctx.respond(
                    embed=embed.build(),
                    view=staffAppsSeeAll(ctx.author, data),
                    ephemeral=True,
                )
            else:
                await ctx.respond(embed=embed.build(), ephemeral=True)
            log(f"{username} viewed all applications")

        elif subcommand == "denied":
            data = self.cursor.execute(
                "select appId, discordName, submissionTime from application where status = 2",
            ).fetchall()
            title = f"Denied Applications page 1/{len(data) // 10 + 1}"
            field_title = "Application ID, Discord Name, Original Submission Time"
            field_content = "".join(
                f"{row[0]}, {row[1]}, {datetime.fromtimestamp(int(row[2]))}\n"
                for row in data[:10]
            )
            fields = [(field_title, field_content, False)]
            embed = EmbedBuilder(
                title=title,
                description="",
                fields=fields,
                color=0x9D0006,
            )  # soft red
            if len(data) > 10:
                await ctx.respond(
                    embed=embed.build(),
                    view=staffAppsSeeDeniedAccepted(ctx.author, data, "d"),
                    ephemeral=True,
                )
            else:
                await ctx.respond(embed=embed.build(), ephemeral=True)
            log(f"{username} viewed denied applications")

        elif subcommand == "accepted":
            data = self.cursor.execute(
                "select appId, discordName, submissionTime from application where status = 9",
            ).fetchall()
            title = f"Accepted Applications page 1/{len(data) // 10 + 1}"
            field_title = "Application ID, Discord Name, Original Submission Time"
            field_content = ""
            for row in data[:10]:
                field_content += (
                    f"{row[0]}, {row[1]}, {datetime.fromtimestamp(int(row[2]))}\n"
                )
            fields = [(field_title, field_content, False)]
            embed = EmbedBuilder(
                title=title,
                description="",
                fields=fields,
                color=0x80C545,
            )  # hwh green
            if len(data) > 10:
                await ctx.respond(
                    embed=embed.build(),
                    view=staffAppsSeeDeniedAccepted(ctx.author, data, "a"),
                    ephemeral=True,
                )
            else:
                await ctx.respond(embed=embed.build(), ephemeral=True)
            log(f"{username} viewed accepted applications")

        elif subcommand == "spam":
            data = self.cursor.execute(
                "select * from user where markedSpam = 1",
            ).fetchall()

            if len(data) == 0:
                await ctx.respond(
                    "No users are currently marked as spam.",
                    ephemeral=True,
                )
                return

            first_user_data = self.cursor.execute(
                "select * from application where uid = ?",
                (data[0][0],),
            ).fetchall()
            count = len(first_user_data)
            name = first_user_data[0][3]
            most_recent = datetime.fromtimestamp(
                max(int(data[10]) for data in first_user_data),
            )

            title = f"Banned users / Marked as spam page 1/{len(data)}"
            field_content = f"Application count: **{count}**\nMost recent application: **{most_recent}**\n"
            fields = [(name, field_content, False)]
            embed = EmbedBuilder(
                title=title,
                description="",
                fields=fields,
                color=0xDD4C35,
            )  # red

            if len(data) > 1:
                await ctx.respond(
                    embed=embed.build(),
                    view=staffAppsSeeSpam(ctx.author, data),
                    ephemeral=True,
                )
            else:
                await ctx.respond(
                    embed=embed.build(),
                    view=staffAppsSeeSpamSimple(data[0][0]),
                    ephemeral=True,
                )
            log(f"{username} viewed banned users")

        else:  # main command, no subcommand
            # gather all active applications
            data = self.cursor.execute(
                "select * from application where status not in (2,9)",
            ).fetchall()
            title = "All current active applications"
            description = "In this embed, you can view all active applications and their status.\nYou can use the buttons below to change the status of an application."
            embed = EmbedBuilder(
                title=title,
                description=description,
                color=0xED75FF,
            )  # pink
            await ctx.respond(
                embed=embed.build(),
                view=staffAppsMain(ctx.author, data),
                ephemeral=True,
            )
            log(f"{username} viewed all active applications")


def setup(bot: commands.Bot) -> None:
    bot.add_cog(StaffAppsBackoffice(bot))
