from discord.ext import commands
from discord import app_commands
from cogs.utils import mongo, embeds
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

    @app_commands.command()
    async def balance(self, interaction: discord.Interaction) -> None:
        """Check your coin balance"""
        guild_name = interaction.guild.name
        title = f'{guild_name}\'s economy'

        guild_id = interaction.guild_id
        guild = mongo.Guild(guild_id)
        guild_info = await guild.check()

        emoji = guild_info.get('emoji', None)
        if emoji is None:
            description = (
                'An admin needs to set up the emoji that '
                'will act as a coin first'
            )
            embed = embeds.simple_embed(title, description)
            await interaction.response.send_message(
                embed=embed, ephemeral=True
            )
            return

        user = mongo.User(interaction.user.id)
        user_info = await user.check()

        economy_info = user_info.get('economy', {})
        guild_economy = economy_info.get(str(guild_id), {})
        balance = guild_economy.get('balance', 0)

        description = f'Your balance is {balance} coins'
        embed = embeds.simple_embed(title, description)
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command()
    async def support(self, interaction: discord.Interaction) -> None:
        """Do you have any question?"""
        title = 'Support server'
        description = f'[[Click here]]({self.server_invite})'
        embed = embeds.simple_embed(title, description)
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command()
    async def invite(self, interaction: discord.Interaction) -> None:
        """Add the bot to your server"""
        title = 'Add bot'
        description = f'[[Click here]]({self.bot_invite})'
        embed = embeds.simple_embed(title, description)
        await interaction.response.send_message(embed=embed, ephemeral=True)


async def setup(bot: Bot) -> None:
    await bot.add_cog(Users(bot))
