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
        welcome = guild_info.get('welcome', False)

        if welcome is True:
            content = 'Welcome messages are already enabled'
            embed = self.simple_embed(content)
            await interaction.response.send_message(
                embed=embed, ephemeral=True
            )
            return

        await guild.update({'welcome': True})
        content = 'Welcome messages have been enabled'
        embed = self.simple_embed(content)
        await interaction.response.send_message(embed=embed, ephemeral=True)


async def setup(bot: Bot) -> None:
    await bot.add_cog(Welcome(bot))
