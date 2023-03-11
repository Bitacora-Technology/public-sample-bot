from discord.ext import commands
from discord import app_commands
from bot import Bot


@app_commands.guild_only()
@app_commands.default_permissions(administrator=True)
class Tickets(commands.GroupCog, group_name='tickets'):
    def __init__(self, bot: Bot) -> None:
        self.bot = bot


async def setup(bot: Bot) -> None:
    await bot.add_cog(Tickets(bot))
