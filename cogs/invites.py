from discord.ext import commands
from discord import app_commands
import discord
from bot import Bot


@app_commands.guild_only()
class Invites(commands.GroupCog, group_name='invites'):
    def __init__(self, bot: Bot) -> None:
        self.bot = bot


async def setup(bot: Bot) -> None:
    await bot.add_cog(Invites(bot))
