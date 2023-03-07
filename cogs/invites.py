from discord.ext import commands
from discord import app_commands
from cogs.utils import mongo
from bot import Bot
import discord


@app_commands.guild_only()
class Invites(commands.GroupCog, group_name='invites'):
    def __init__(self, bot: Bot) -> None:
        self.bot = bot

    @app_commands.command()
    async def create(self, interaction: discord.Interaction) -> None:
        """Get your own server invite"""
        user_id = interaction.user.id
        guild_id = str(interaction.guild_id)

        user = mongo.User(user_id)
        user_info = await user.check()

        guild_dict = user_info.get('invites', {})
        guild_info = guild_dict.get(guild_id, {})
        user_invite = guild_info.get('url', None)

        if user_invite is not None:
            invite_list = await interaction.guild.invites()
            invite_exists = discord.utils.get(invite_list, url=user_invite)
            if bool(invite_exists) is True:
                content = f'<{user_invite}>'
                await interaction.response.send_message(
                    content, ephemeral=True
                )
                return

        create_result = await interaction.channel.create_invite()
        user_invite = create_result.url
        query = {f'invites.{guild_id}.url': user_invite}
        await user.update(query)

        content = f'<{user_invite}>'
        await interaction.response.send_message(content, ephemeral=True)


async def setup(bot: Bot) -> None:
    await bot.add_cog(Invites(bot))
