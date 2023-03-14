from discord.ext import commands
from discord import app_commands
from cogs.utils import mongo, formatting
from bot import Bot
import discord


@app_commands.guild_only()
class Users(commands.Cog):
    def __init__(self, bot: Bot) -> None:
        self.bot = bot
        self.server_invite = 'https://discord.gg/AV2F74vSDx'
        self.bot_invite = (
            'https://discord.com/api/oauth2/authorize?client_id='
            '1085024816119156808&permissions=8&scope=bot%20'
            'applications.commands'
        )

    @app_commands.command()
    async def help(self, interaction: discord.Interaction) -> None:
        """Get the most out of the bot"""
        content = 'Work in progress'
        await interaction.response.send_message(content, ephemeral=True)

    def simple_embed(self, title: str, description: str) -> discord.Embed:
        embed = discord.Embed(
            title=title,
            description=description,
            color=formatting.embed_color_dec
        )
        embed.set_footer(
            text='https://bitacora.gg', icon_url=formatting.bot_avatar_url
        )

        return embed

    @app_commands.command()
    async def balance(self, interaction: discord.Interaction) -> None:
        """Check your coin balance"""
        user = mongo.User(interaction.user.id)
        user_info = await user.check()

        economy_info = user_info.get('economy', {})
        guild_economy = economy_info.get(str(interaction.guild_id), {})
        balance = guild_economy.get('balance', None)

        guild = mongo.Guild(interaction.guild_id)
        guild_info = await guild.check()
        emoji = guild_info.get('emoji', '')

        content = f'Your balance is {balance} {emoji}'
        embed = self.simple_embed('Coin balance', content)
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command()
    async def support(self, interaction: discord.Interaction) -> None:
        """Do you have any question?"""
        content = f'[[Click here]]({self.server_invite})'
        embed = self.simple_embed('Support server', content)
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command()
    async def invite(self, interaction: discord.Interaction) -> None:
        """Add the bot to your server"""
        content = f'[[Click here]]({self.bot_invite})'
        embed = self.simple_embed('Add bot', content)
        await interaction.response.send_message(embed=embed, ephemeral=True)


async def setup(bot: Bot) -> None:
    await bot.add_cog(Users(bot))
