from discord.ext import commands
from discord import app_commands
from cogs.utils import embeds
from importlib import reload
from asyncio import sleep
from bot import Bot
import discord


embed_title = 'Support tickets'


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

            description = (
                f'Thanks for reaching out, {user.mention}. We will '
                'assist you as soon as we are available.'
            )
            embed = embeds.simple_embed(embed_title, description)
            await channel.send(embed=embed)

        description = f'You can find your ticket at {channel.mention}'
        embed = embeds.simple_embed(embed_title, description)
        await interaction.response.send_message(embed=embed, ephemeral=True)


class OpenTicketView(discord.ui.View):
    def __init__(self) -> None:
        super().__init__(timeout=None)
        self.add_item(OpenTicketButton())


@app_commands.guild_only()
@app_commands.default_permissions(administrator=True)
class Tickets(commands.GroupCog, group_name='tickets'):
    def __init__(self, bot: Bot) -> None:
        self.bot = bot
        self.category_name = 'Tickets'

    async def cog_load(self) -> None:
        module_list = [embeds]
        for module in module_list:
            reload(module)

        view_list = [OpenTicketView()]
        for view in view_list:
            self.bot.add_view(view)

    @app_commands.command()
    async def panel(self, interaction: discord.Interaction) -> None:
        """Send a ticket panel"""
        description = 'Click the button bellow to open a ticket'
        embed = embeds.simple_embed(embed_title, description)
        view = OpenTicketView()
        await interaction.channel.send(embed=embed, view=view)

        description = 'Ticket panel sent'
        embed = embeds.simple_embed(embed_title, description)
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command()
    async def close(self, interaction: discord.Interaction) -> None:
        """Close the ticket"""
        category = interaction.channel.category
        if category is None or category.name != self.category_name:
            description = (
                'The command only works at the '
                f'\'{self.category_name}\' category'
            )
            embed = embeds.simple_embed(embed_title, description)
            await interaction.response.send_message(
                embed=embed, ephemeral=True
            )
            return

        user = interaction.user
        description = f'Closing ticket as requested by {user.mention}'
        embed = embeds.simple_embed(embed_title, description)
        await interaction.response.send_message(embed=embed)

        await sleep(5)
        await interaction.channel.delete()


async def setup(bot: Bot) -> None:
    await bot.add_cog(Tickets(bot))
