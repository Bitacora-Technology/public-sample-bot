from discord.ext import commands
from discord import app_commands
from cogs.utils import mongo, formatting
from bot import Bot
import discord


@app_commands.guild_only()
class Users(commands.Cog):
    def __init__(self, bot: Bot) -> None:
        self.bot = bot

    @app_commands.command()
    async def help(self, interaction: discord.Interaction) -> None:
        """Get the most out of the bot"""

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
        await interaction.response.send_message(content, ephemeral=True)


async def setup(bot: Bot) -> None:
    await bot.add_cog(Users(bot))
