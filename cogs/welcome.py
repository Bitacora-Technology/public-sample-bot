from discord.ext import commands
from discord import app_commands
from cogs.utils import mongo, embeds
from importlib import reload
from bot import Bot
import discord


@app_commands.guild_only()
@app_commands.default_permissions(administrator=True)
class Welcome(commands.GroupCog, group_name='welcome'):
    def __init__(self, bot: Bot) -> None:
        self.bot = bot
        self.embed_title = '{}\'s welcome'

    async def cog_load(self) -> None:
        module_list = [mongo, embeds]
        for module in module_list:
            reload(module)

    @app_commands.command()
    async def enable(self, interaction: discord.Interaction) -> None:
        """Enable the welcome messages"""
        guild = mongo.Guild(interaction.guild_id)
        guild_info = await guild.check()

        welcome_info = guild_info.get('welcome', {})
        enabled = welcome_info.get('enabled', False)

        guild_name = interaction.guild.name
        title = self.embed_title.format(guild_name)

        if enabled is True:
            description = 'Welcome messages are already enabled'
            embed = embeds.simple_embed(title, description)
            await interaction.response.send_message(
                embed=embed, ephemeral=True
            )
            return

        await guild.update({'welcome.enabled': True})

        description = 'Welcome messages have been enabled'
        embed = embeds.simple_embed(title, description)
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command()
    async def disable(self, interaction: discord.Interaction) -> None:
        """Disable the welcome messages"""
        guild = mongo.Guild(interaction.guild_id)
        guild_info = await guild.check()

        welcome_info = guild_info.get('welcome', {})
        enabled = welcome_info.get('enabled', False)

        guild_name = interaction.guild.name
        title = self.embed_title.format(guild_name)

        if enabled is False:
            description = 'Welcome messages are already disabled'
            embed = embed = embeds.simple_embed(title, description)
            await interaction.response.send_message(
                embed=embed, ephemeral=True
            )
            return

        await guild.update({'welcome.enabled': False})
        description = 'Welcome messages have been disabled'
        embed = embed = embeds.simple_embed(title, description)
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command()
    @app_commands.describe(channel='The arrivals channel')
    async def set(
        self, interaction: discord.Interaction, channel: discord.TextChannel
    ) -> None:
        """Set where the messages will be sent"""
        guild = mongo.Guild(interaction.guild_id)
        await guild.update({'welcome.channel': channel.id})

        guild_name = interaction.guild.name
        title = self.embed_title.format(guild_name)

        description = f'The channel {channel.mention} has been set'
        embed = embeds.simple_embed(title, description)
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @commands.GroupCog.listener()
    async def on_member_join(self, member: discord.Member) -> None:
        guild = mongo.Guild(member.guild.id)
        guild_info = await guild.check()

        welcome_info = guild_info.get('welcome', {})
        enabled = welcome_info.get('enabled', False)
        channel_id = welcome_info.get('channel', None)

        if enabled is False or channel_id is None:
            return

        channel = member.guild.get_channel(channel_id)
        if channel is None:
            channel = member.guild.fetch_channel(channel_id)

        embed = embeds.welcome_embed(member)
        await channel.send(embed=embed)


async def setup(bot: Bot) -> None:
    await bot.add_cog(Welcome(bot))
