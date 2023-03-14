from discord.ext import commands
from discord import app_commands
from cogs.utils import embeds as _embeds
from importlib import reload
from bot import Bot
import discord


class CreateEmbedModal(discord.ui.Modal):
    def __init__(self) -> None:
        super().__init__(title='Create embed')

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
            'thumbnail_url': ''
        }

        embed = _embeds.advanced_embed(embed_info)
        view = ConfigureEmbedView(embed_info)
        await interaction.response.send_message(
            embed=embed, view=view, ephemeral=True
        )


class AddFieldModal(discord.ui.Modal):
    def __init__(self, embed_info: dict) -> None:
        super().__init__(title='Add field')
        self.embed_info = embed_info

    name = discord.ui.TextInput(label='Name', max_length=256)

    value = discord.ui.TextInput(
        label='Value', style=discord.TextStyle.long, max_length=1024
    )

    async def on_submit(self, interaction: discord.Interaction) -> None:
        field = {
            'name': self.name.value,
            'value': self.value.value
        }
        self.embed_info['field_list'].append(field)

        embed = _embeds.advanced_embed(self.embed_info)
        view = ManageFieldsView(self.embed_info)
        await interaction.response.edit_message(embed=embed, view=view)


class AddFieldButton(discord.ui.Button):
    def __init__(self, embed_info: dict) -> None:
        super().__init__(
            label='Add field', style=discord.ButtonStyle.success
        )
        self.embed_info = embed_info

    async def callback(self, interaction: discord.Interaction) -> None:
        modal = AddFieldModal(self.embed_info)
        await interaction.response.send_modal(modal)


class RemoveFieldDropdown(discord.ui.Select):
    def __init__(self, embed_info: dict) -> None:
        options = []
        field_list = embed_info['field_list']
        count = 0
        for field in field_list:
            options.append(
                discord.SelectOption(
                    label=field['name'][:100],
                    description=field['value'][:100],
                    value=str(count)
                )
            )
            count += 1
        super().__init__(
            placeholder='Choose the fields to remove...',
            min_values=1,
            max_values=len(field_list),
            options=options
        )
        self.embed_info = embed_info

    async def callback(self, interaction: discord.Interaction) -> None:
        self.values.sort()
        self.values.reverse()
        for value in self.values:
            self.embed_info['field_list'].pop(int(value))

        embed = _embeds.advanced_embed(self.embed_info)
        view = ManageFieldsView(self.embed_info)
        await interaction.response.edit_message(embed=embed, view=view)


class BackFieldsButton(discord.ui.Button):
    def __init__(self, embed_info: dict) -> None:
        super().__init__(label='Go back')
        self.embed_info = embed_info

    async def callback(self, interaction: discord.Interaction) -> None:
        embed = _embeds.advanced_embed(self.embed_info)
        view = ManageFieldsView(self.embed_info)
        await interaction.response.edit_message(embed=embed, view=view)


class RemoveFieldView(discord.ui.View):
    def __init__(self, embed_info: dict) -> None:
        super().__init__(timeout=None)
        self.add_item(RemoveFieldDropdown(embed_info))
        self.add_item(BackFieldsButton(embed_info))


class RemoveFieldButton(discord.ui.Button):
    def __init__(self, embed_info: dict) -> None:
        super().__init__(
            label='Remove field', style=discord.ButtonStyle.danger
        )
        self.embed_info = embed_info

    async def callback(self, interaction: discord.Interaction) -> None:
        field_list = self.embed_info['field_list']

        if len(field_list) == 0:
            await interaction.response.defer()
        else:
            embed = _embeds.advanced_embed(self.embed_info)
            view = RemoveFieldView(self.embed_info)
            await interaction.response.edit_message(embed=embed, view=view)


class BackConfigureButton(discord.ui.Button):
    def __init__(self, embed_info: dict) -> None:
        super().__init__(label='Go back')
        self.embed_info = embed_info

    async def callback(self, interaction: discord.Interaction) -> None:
        embed = _embeds.advanced_embed(self.embed_info)
        view = ConfigureEmbedView(self.embed_info)
        await interaction.response.edit_message(embed=embed, view=view)


class ManageFieldsView(discord.ui.View):
    def __init__(self, embed_info: dict) -> None:
        super().__init__(timeout=None)
        self.add_item(AddFieldButton(embed_info))
        self.add_item(RemoveFieldButton(embed_info))
        self.add_item(BackConfigureButton(embed_info))


class ManageFieldsButton(discord.ui.Button):
    def __init__(self, embed_info: dict) -> None:
        super().__init__(
            label='Manage fields', style=discord.ButtonStyle.primary
        )
        self.embed_info = embed_info

    async def callback(self, interaction: discord.Interaction) -> None:
        embed = _embeds.advanced_embed(self.embed_info)
        view = ManageFieldsView(self.embed_info)
        await interaction.response.edit_message(embed=embed, view=view)


class AddImageModal(discord.ui.Modal):
    def __init__(self, embed_info: dict) -> None:
        super().__init__(title='Add image')
        self.embed_info = embed_info

    url = discord.ui.TextInput(label='Url')

    async def on_submit(self, interaction: discord.Interaction) -> None:
        self.embed_info['image_url'] = self.url.value

        embed = _embeds.advanced_embed(self.embed_info)
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

            embed = _embeds.advanced_embed(self.embed_info)
            view = ConfigureEmbedView(self.embed_info)
            await interaction.response.edit_message(embed=embed, view=view)


class AddThumbnailModal(discord.ui.Modal):
    def __init__(self, embed_info: dict) -> None:
        super().__init__(title='Add thumbnail')
        self.embed_info = embed_info

    url = discord.ui.TextInput(label='Url')

    async def on_submit(self, interaction: discord.Interaction) -> None:
        self.embed_info['thumbnail_url'] = self.url.value

        embed = _embeds.advanced_embed(self.embed_info)
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

            embed = _embeds.advanced_embed(self.embed_info)
            view = ConfigureEmbedView(self.embed_info)
            await interaction.response.edit_message(embed=embed, view=view)


class SendEmbedButton(discord.ui.Button):
    def __init__(self, embed_info: dict) -> None:
        super().__init__(label='Send', style=discord.ButtonStyle.primary)
        self.embed_info = embed_info

    async def callback(self, interaction: discord.Interaction) -> None:
        embed = _embeds.advanced_embed(self.embed_info)
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

    async def cog_load(self) -> None:
        module_list = [_embeds]
        for module in module_list:
            reload(module)

    @app_commands.command()
    async def send(self, interaction: discord.Interaction) -> None:
        """Send a custom embed"""
        modal = CreateEmbedModal()
        await interaction.response.send_modal(modal)


async def setup(bot: Bot) -> None:
    await bot.add_cog(Embeds(bot))
