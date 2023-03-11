from discord.ext import commands
from discord import app_commands
from cogs.utils import formatting
from bot import Bot
import discord


class OpenTicketButton(discord.ui.Button):
    def __init__(self) -> None:
        super().__init__(
            emoji='✉️',
            style=discord.ButtonStyle.primary,
            custom_id='open-ticket'
        )
        self.category_name = 'Tickets'

    async def callback(self, interaction: discord.Interaction) -> None:
        category = discord.utils.get(
            interaction.guild.categories, name=self.category_name
        )

        default_role = interaction.guild.default_role
        overwrites = {
            default_role: discord.PermissionOverwrite(view_channel=False)
        }
        if bool(category) is False:
            category = await interaction.guild.create_category(
                self.category_name, overwrites=overwrites
            )

        user = interaction.user
        channel_name = f'{user.name}-{user.discriminator}'.lower()

        channel = discord.utils.get(
            interaction.guild.text_channels, name=channel_name
        )
        if bool(channel) is False:
            overwrites[user] = discord.PermissionOverwrite(view_channel=True)
            channel = await category.create_text_channel(
                channel_name, overwrites=overwrites
            )

            content = (
                f'Thanks for reaching out, {user.mention}. We will '
                'assist you as soon as we are available.'
            )
            await channel.send(content)

        content = f'You can find your ticket at {channel.mention}'
        await interaction.response.send_message(content, ephemeral=True)


class OpenTicketView(discord.ui.View):
    def __init__(self) -> None:
        super().__init__(timeout=None)
        self.add_item(OpenTicketButton())


@app_commands.guild_only()
@app_commands.default_permissions(administrator=True)
class Tickets(commands.GroupCog, group_name='tickets'):
    def __init__(self, bot: Bot) -> None:
        self.bot = bot

    def panel_embed(self) -> discord.Embed:
        embed = discord.Embed(
            title='Support Tickets',
            description='Click the button bellow to open a ticket',
            color=formatting.embed_color_dec
        )

        embed.set_footer(
            text='https://bitacora.gg', icon_url=formatting.bot_avatar_url
        )

        return embed

    @app_commands.command()
    async def panel(self, interaction: discord.Interaction) -> None:
        """Send a ticket panel"""
        embed = self.panel_embed()
        view = OpenTicketView()
        await interaction.channel.send(embed=embed, view=view)
        content = 'Ticket panel sent'
        await interaction.response.send_message(content, ephemeral=True)


async def setup(bot: Bot) -> None:
    await bot.add_cog(Tickets(bot))
