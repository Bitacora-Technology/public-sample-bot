from discord.ext import commands
from discord import app_commands
from bot import Bot
import discord


def create_embed(embed_info: dict) -> discord.Embed:
    embed = discord.Embed(
        title=embed_info['title'],
        description=embed_info['description'],
        color=embed_info['color']
    )

    embed.set_footer(text='https://bitacora.gg', icon_url=embed_info['avatar'])

    embed.set_image(url=embed_info['image_url'])
    embed.set_thumbnail(url=embed_info['thumbnail_url'])

    field_list = embed_info['field_list']
    for field in field_list:
        embed.add_field(
            name=field['name'], value=field['value'], inline=field['inline']
        )

    return embed


class CreateEmbedModal(discord.ui.Modal):
    def __init__(self, bot: Bot) -> None:
        super().__init__(title='Create embed')
        self.bot = bot

    _title = discord.ui.TextInput(
        label='Title', required=False, max_length=256
    )

    description = discord.ui.TextInput(
        label='Description', style=discord.TextStyle.long, required=False
    )

    async def on_submit(self, interaction: discord.Interaction) -> None:
        embed_info = {
            'title': self._title.value,
            'description': self.description.value,
            'field_list': [],
            'image_url': '',
            'thumbnail_url': '',
            'color': self.bot.color,
            'avatar': self.bot.user.avatar
        }

        embed = create_embed(embed_info)
        view = ConfigureEmbedView(embed_info)
        await interaction.response.send_message(
            embed=embed, view=view, ephemeral=True
        )


class ManageFieldsButton(discord.ui.Button):
    def __init__(self, embed_info: dict) -> None:
        super().__init__(
            label='Manage fields', style=discord.ButtonStyle.primary
        )
        self.embed_info = embed_info


class AddImageModal(discord.ui.Modal):
    def __init__(self, embed_info: dict) -> None:
        super().__init__(title='Add image')
        self.embed_info = embed_info

    url = discord.ui.TextInput(label='Url')

    async def on_submit(self, interaction: discord.Interaction) -> None:
        self.embed_info['image_url'] = self.url.value

        embed = create_embed(self.embed_info)
        view = ConfigureEmbedView(self.embed_info)

        try:
            await interaction.response.edit_message(embed=embed, view=view)
        except Exception:
            content = 'Invalid image url'
            await interaction.channel.send(content, delete_after=5)


class ManageImageButton(discord.ui.Button):
    def __init__(self, embed_info: dict) -> None:
        image_url = embed_info['image_url']

        if image_url == '':
            label = 'Add image'
            style = discord.ButtonStyle.success
            custom_id = 'add-image'

        else:
            label = 'Remove image'
            style = discord.ButtonStyle.danger
            custom_id = 'remove-image'

        super().__init__(label=label, style=style, custom_id=custom_id)
        self.embed_info = embed_info

    async def callback(self, interaction: discord.Interaction) -> None:
        if self.custom_id == 'add-image':
            modal = AddImageModal(self.embed_info)
            await interaction.response.send_modal(modal)

        else:
            self.embed_info['image_url'] = ''

            embed = create_embed(self.embed_info)
            view = ConfigureEmbedView(self.embed_info)
            await interaction.response.edit_message(embed=embed, view=view)


class AddThumbnailModal(discord.ui.Modal):
    def __init__(self, embed_info: dict) -> None:
        super().__init__(title='Add thumbnail')
        self.embed_info = embed_info

    url = discord.ui.TextInput(label='Url')

    async def on_submit(self, interaction: discord.Interaction) -> None:
        self.embed_info['thumbnail_url'] = self.url.value

        embed = create_embed(self.embed_info)
        view = ConfigureEmbedView(self.embed_info)

        try:
            await interaction.response.edit_message(embed=embed, view=view)
        except Exception:
            content = 'Invalid image url'
            await interaction.channel.send(content, delete_after=5)


class ManageThumbnailButton(discord.ui.Button):
    def __init__(self, embed_info: dict) -> None:
        thumbnail_url = embed_info['thumbnail_url']

        if thumbnail_url == '':
            label = 'Add thumbnail'
            style = discord.ButtonStyle.success
            custom_id = 'add-thumbnail'

        else:
            label = 'Remove thumbnail'
            style = discord.ButtonStyle.danger
            custom_id = 'remove-thumbnail'

        super().__init__(label=label, style=style, custom_id=custom_id)
        self.embed_info = embed_info

    async def callback(self, interaction: discord.Interaction) -> None:
        if self.custom_id == 'add-thumbnail':
            modal = AddThumbnailModal(self.embed_info)
            await interaction.response.send_modal(modal)

        else:
            self.embed_info['thumbnail_url'] = ''

            embed = create_embed(self.embed_info)
            view = ConfigureEmbedView(self.embed_info)
            await interaction.response.edit_message(embed=embed, view=view)


class SendEmbedButton(discord.ui.Button):
    def __init__(self, embed_info: dict) -> None:
        super().__init__(label='Send', style=discord.ButtonStyle.primary)
        self.embed_info = embed_info

    async def callback(self, interaction: discord.Interaction) -> None:
        embed = create_embed(self.embed_info)
        await interaction.channel.send(embed=embed)
        await interaction.response.defer()


class ConfigureEmbedView(discord.ui.View):
    def __init__(self, embed_info: dict) -> None:
        super().__init__(timeout=None)
        self.add_item(ManageFieldsButton(embed_info))
        self.add_item(ManageImageButton(embed_info))
        self.add_item(ManageThumbnailButton(embed_info))
        self.add_item(SendEmbedButton(embed_info))


@app_commands.guild_only()
@app_commands.default_permissions(administrator=True)
class Embeds(commands.GroupCog, group_name='embeds'):
    def __init__(self, bot: Bot) -> None:
        self.bot = bot

    @app_commands.command()
    async def create(self, interaction: discord.Interaction) -> None:
        """Send a custom embed"""
        modal = CreateEmbedModal(self.bot)
        await interaction.response.send_modal(modal)


async def setup(bot: Bot) -> None:
    await bot.add_cog(Embeds(bot))
