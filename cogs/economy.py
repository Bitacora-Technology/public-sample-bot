from discord.ext import commands
from discord import app_commands
from bot import Bot


@app_commands.guild_only()
class Economy(commands.GroupCog, group_name='economy'):
    def __init__(self, bot: Bot) -> None:
        self.bot = bot
        self.invites = {}


async def setup(bot: Bot) -> None:
    await bot.add_cog(Economy(bot))
