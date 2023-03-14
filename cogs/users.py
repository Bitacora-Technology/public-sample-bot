from discord.ext import commands
from discord import app_commands
from bot import Bot


@app_commands.guild_only()
class Users(commands.Cog):
    def __init__(self, bot: Bot) -> None:
        self.bot = bot


async def setup(bot: Bot) -> None:
    await bot.add_cog(Users(bot))
