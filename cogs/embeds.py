from discord.ext import commands
from discord import app_commands
from bot import Bot
import discord


def create_embed(bot: Bot, embed_info: dict) -> discord.Embed:
    embed = discord.Embed(
        title=embed_info['title'],
        description=embed_info['description'],
        color=bot.color
    )

    embed.set_footer(text='https://bitacora.gg', icon_url=bot.user.avatar)

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
            'thumbnail_url': ''
        }

        embed = create_embed(self.bot, embed_info)
        await interaction.response.send_message(embed=embed, ephemeral=True)


@app_commands.guild_only()
@app_commands.default_permissions(administrator=True)
class Embeds(commands.GroupCog, group_name='embeds'):
    def __init__(self, bot: Bot) -> None:
        self.bot = bot

    @app_commands.command()
    async def send(self, interaction: discord.Interaction) -> None:
        """Create a custom embed"""
        modal = CreateEmbedModal(self.bot)
        await interaction.response.send_modal(modal)


async def setup(bot: Bot) -> None:
    await bot.add_cog(Embeds(bot))
