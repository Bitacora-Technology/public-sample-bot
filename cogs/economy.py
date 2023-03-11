from discord.ext import commands
from discord import app_commands
from asyncio import TimeoutError
from cogs.utils import mongo
from bot import Bot
import discord


@app_commands.guild_only()
@app_commands.default_permissions(administrator=True)
class Economy(commands.GroupCog, group_name='economy'):
    def __init__(self, bot: Bot) -> None:
        self.bot = bot

    @app_commands.command()
    async def coin(self, interaction: discord.Interaction) -> None:
        """Set which emoji will act as coin"""
        await interaction.response.defer(ephemeral=True, thinking=True)
        content = 'React with the emoji you want to use'
        message = await interaction.channel.send(content)

        def check(reaction: discord.Reaction, user: discord.User) -> bool:
            return (
                user.id == interaction.user.id and
                message.id == reaction.message.id
            )

        try:
            reaction = await self.bot.wait_for(
                'reaction_add', check=check, timeout=90
            )
        except TimeoutError:
            content = 'No reaction was received'
            await interaction.followup.send(content)
            await message.delete()
            return

        emoji = str(reaction[0].emoji)
        await message.delete()

        guild = mongo.Guild(interaction.guild_id)
        await guild.update({'emoji': emoji})

        content = f'Emoji {emoji} has been set as coin'
        await interaction.followup.send(content)


async def setup(bot: Bot) -> None:
    await bot.add_cog(Economy(bot))
