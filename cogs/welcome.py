from discord.ext import commands
from discord import app_commands
from cogs.utils import mongo, formatting
from bot import Bot
import discord


@app_commands.guild_only()
@app_commands.default_permissions(administrator=True)
class Welcome(commands.GroupCog, group_name='welcome'):
    def __init__(self, bot: Bot) -> None:
        self.bot = bot

    def simple_embed(self, description: str) -> discord.Embed:
        embed = discord.Embed(
            title='Welcome',
            description=description,
            color=formatting.embed_color_dec
        )
        embed.set_footer(
            text='https://bitacora.gg', icon_url=formatting.bot_avatar_url
        )
        return embed

    @app_commands.command()
    async def enable(self, interaction: discord.Interaction) -> None:
        """Enable the welcome messages"""
        guild = mongo.Guild(interaction.guild_id)
        guild_info = await guild.check()
        welcome_info = guild_info.get('welcome', {})
        enabled = welcome_info.get('enabled', False)

        if enabled is True:
            content = 'Welcome messages are already enabled'
            embed = self.simple_embed(content)
            await interaction.response.send_message(
                embed=embed, ephemeral=True
            )
            return

        await guild.update({'welcome.enabled': True})
        content = 'Welcome messages have been enabled'
        embed = self.simple_embed(content)
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command()
    async def disable(self, interaction: discord.Interaction) -> None:
        """Disable the welcome messages"""
        guild = mongo.Guild(interaction.guild_id)
        guild_info = await guild.check()
        welcome_info = guild_info.get('welcome', {})
        enabled = welcome_info.get('enabled', False)

        if enabled is False:
            content = 'Welcome messages are already disabled'
            embed = self.simple_embed(content)
            await interaction.response.send_message(
                embed=embed, ephemeral=True
            )
            return

        await guild.update({'welcome.enabled': False})
        content = 'Welcome messages have been disabled'
        embed = self.simple_embed(content)
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command()
    @app_commands.describe(channel='The arrivals channel')
    async def set(
        self, interaction: discord.Interaction, channel: discord.TextChannel
    ) -> None:
        """Set where the messages will be sent"""
        guild = mongo.Guild(interaction.guild_id)
        await guild.update({'welcome.channel': channel.id})

        content = f'The channel {channel.mention} has been set'
        await interaction.response.send_message(content, ephemeral=True)

    def member_embed(self, member: discord.Member) -> discord.Member:
        embed = discord.Embed(
            title='New Arrival',
            color=formatting.embed_color_dec
        )
        embed.add_field(
            name='Member', value=f'{member.name}#{member.discriminator}'
        )
        embed.set_footer(
            text='https://bitacora.gg', icon_url=formatting.bot_avatar_url
        )
        embed.set_thumbnail(url=member.avatar)

        return embed

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

        embed = self.member_embed(member)
        await channel.send(embed=embed)


async def setup(bot: Bot) -> None:
    await bot.add_cog(Welcome(bot))
