from discord.ext import commands
from discord import app_commands
from cogs.utils import mongo
from bot import Bot
import discord


@app_commands.guild_only()
class Invites(commands.GroupCog, group_name='invites'):
    def __init__(self, bot: Bot) -> None:
        self.bot = bot
        self.invites = {}

    async def check_global_invites(self) -> None:
        for guild in self.bot.guilds:
            guild_dict = {}
            guild_id = str(guild.id)
            invite_list = await guild.invites()
            for invite in invite_list:
                guild_dict[invite.url] = invite.uses
            self.invites[guild_id] = guild_dict

    @commands.GroupCog.listener()
    async def on_ready(self) -> None:
        await self.bot.wait_until_ready()
        await self.check_global_invites()

    def simple_embed(self, title: str, description: str) -> discord.Embed:
        embed = discord.Embed(
            title=title,
            description=description,
            color=self.bot.color
        )
        embed.set_footer(
            text='https://bitacora.gg', icon_url=self.bot.user.avatar
        )
        return embed

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

        if bool(user_invite) is True:
            invite_list = await interaction.guild.invites()
            invite_exists = discord.utils.get(invite_list, url=user_invite)
            if bool(invite_exists) is True:
                title = 'Invite'
                content = f'<{user_invite}>'
                embed = self.simple_embed(title, content)
                await interaction.response.send_message(
                    embed=embed, ephemeral=True
                )
                return

        create_result = await interaction.channel.create_invite()
        user_invite = create_result.url
        query = {f'invites.{guild_id}.url': user_invite}
        await user.update(query)
        await self.check_global_invites()

        title = 'Invite'
        content = f'<{user_invite}>'
        embed = self.simple_embed(title, content)
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command()
    async def stats(self, interaction: discord.Interaction) -> None:
        """Check how many users you invited"""
        user_id = interaction.user.id
        guild_id = str(interaction.guild_id)

        user = mongo.User(user_id)
        user_info = await user.check()

        guild_dict = user_info.get('invites', {})
        guild_info = guild_dict.get(guild_id, {})
        invite_count = guild_info.get('count', 0)

        if invite_count == 1:
            users = 'user'
        else:
            users = 'users'

        title = 'Stats'
        content = f'You have invited {invite_count} {users}'
        embed = self.simple_embed(title, content)
        await interaction.response.send_message(embed=embed, ephemeral=True)

    async def check_guild_invites(
        self, guild: discord.Guild
    ) -> tuple[dict, list]:
        invites = {}
        invite_list = await guild.invites()
        for invite in invite_list:
            invites[invite.url] = invite.uses
        return invites, invite_list

    @commands.GroupCog.listener()
    async def on_member_join(self, member: discord.Member):
        guild_id = str(member.guild.id)
        guild_invites, invite_list = await self.check_guild_invites(
            member.guild
        )

        invite_url = None
        for key in guild_invites.keys() & self.invites[guild_id].keys():
            old_value = self.invites[guild_id].get(key, None)
            new_value = guild_invites.get(key, None)
            if new_value - 1 == old_value:
                invite_url = key
        await self.check_global_invites()

        if invite_url is None:
            return

        invited_by = None
        user_cursor = mongo.User().cursor()
        async for user_info in user_cursor:
            guild_dict = user_info.get('invites', {})
            guild_info = guild_dict.get(guild_id, {})
            user_invite = guild_info.get('url', None)
            if user_invite == invite_url:
                invited_by = user_info['_id']

        if invited_by is None:
            return

        user = mongo.User(invited_by)
        await user.update({f'invites.{guild_id}.count': 1}, method='inc')


async def setup(bot: Bot) -> None:
    await bot.add_cog(Invites(bot))
