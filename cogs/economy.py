from discord.ext import commands
from discord import app_commands
from asyncio import TimeoutError
from cogs.utils import mongo, formatting
from importlib import reload
from bot import Bot
import discord


class CheckBalanceButton(discord.ui.Button):
    def __init__(self) -> None:
        super().__init__(
            label='My balance',
            custom_id='check-balance',
            style=discord.ButtonStyle.primary
        )

    def balance_embed(self, balance: int, emoji: str) -> discord.Embed:
        embed = discord.Embed(
            title='Coin balance',
            description=f'Your balance is {balance} {emoji}',
            color=formatting.embed_color_dec
        )

        embed.set_footer(
            text='https://bitacora.gg', icon_url=formatting.bot_avatar_url
        )

        return embed

    async def callback(self, interaction: discord.Interaction) -> None:
        user_id = interaction.user.id
        guild_id = interaction.guild_id

        guild = mongo.Guild(guild_id)
        guild_info = await guild.check()

        emoji = guild_info.get('emoji', '')

        user = mongo.User(user_id)
        user_info = await user.check()

        economy_dict = user_info.get('economy', {})
        guild_info = economy_dict.get(str(guild_id), {})
        balance = guild_info.get('balance', 0)

        embed = self.balance_embed(balance, emoji)
        await interaction.response.send_message(embed=embed, ephemeral=True)


class GuildLeaderboardButton(discord.ui.Button):
    def __init__(self) -> None:
        super().__init__(
            label='Leaderboard',
            custom_id='guild-leaderboard',
            style=discord.ButtonStyle.primary
        )

    def leaderboard_embed(
        self, leaderboard: list, emoji: str
    ) -> discord.Embed:
        descripion = ''
        for index in range(0, len(leaderboard) - 1):
            user = leaderboard[index]
            user_id = user['id']
            balance = user['balance']
            descripion += f'{index + 1}. <@{user_id}> - {balance} {emoji}'

        embed = discord.Embed(
            title='Coin leaderboard',
            description=descripion,
            color=formatting.embed_color_dec
        )

        embed.set_footer(
            text='https://bitacora.gg', icon_url=formatting.bot_avatar_url
        )

        return embed

    async def callback(self, interaction: discord.Interaction) -> None:
        guild_id = str(interaction.guild_id)
        users = mongo.User()
        cursor = users.cursor()

        user_list = []
        async for user_info in cursor:
            economy_info = user_info.get('economy', {})
            guild_info = economy_info.get(guild_id, None)

            if guild_info is None:
                continue

            user_item = {
                'id': user_info['_id'],
                'balance': guild_info['balance']
            }
            user_list.append(user_item)

        guild = mongo.Guild(interaction.guild_id)
        guild_info = await guild.check()
        emoji = guild_info.get('emoji', '')

        leaderboard = sorted(
            user_list, key=lambda u: u['balance'], reverse=True
        )[:10]

        embed = self.leaderboard_embed(leaderboard, emoji)
        await interaction.response.send_message(embed=embed, ephemeral=True)


class EconomyPanelView(discord.ui.View):
    def __init__(self) -> None:
        super().__init__(timeout=None)
        self.add_item(CheckBalanceButton())
        self.add_item(GuildLeaderboardButton())


@app_commands.guild_only()
@app_commands.default_permissions(administrator=True)
class Economy(commands.GroupCog, group_name='economy'):
    def __init__(self, bot: Bot) -> None:
        self.bot = bot

    async def cog_load(self) -> None:
        module_list = [mongo, formatting]
        for module in module_list:
            reload(module)

        view_list = [EconomyPanelView()]
        for view in view_list:
            self.bot.add_view(view)

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

    def panel_embed(self, emoji: str) -> discord.Embed:
        embed = discord.Embed(
            title='Economy',
            description=(
                'You can give a coin to an user reacting '
                f'to his message with emoji {emoji}'
            ),
            color=formatting.embed_color_dec
        )

        embed.set_footer(
            text='https://bitacora.gg', icon_url=formatting.bot_avatar_url
        )

        return embed

    @app_commands.command()
    async def panel(self, interaction: discord.Interaction) -> None:
        """Send an economy panel"""
        guild = mongo.Guild(interaction.guild_id)
        guild_info = await guild.check()

        emoji = guild_info.get('emoji', '')
        if emoji == '':
            content = 'Economy hasn\'t been configured yet'
            await interaction.response.send_message(content, ephemeral=True)
            return

        embed = self.panel_embed(emoji)
        view = EconomyPanelView()
        await interaction.channel.send(embed=embed, view=view)
        content = 'Economy panel sent'
        await interaction.response.send_message(content, ephemeral=True)

    async def find_receiver(self, channel_id: int, message_id: int) -> int:
        channel = self.bot.get_channel(channel_id)
        if channel is None:
            channel = await self.bot.fetch_channel(channel_id)

        message = await channel.fetch_message(message_id)
        return message.author.id

    @commands.Cog.listener()
    async def on_raw_reaction_add(
        self, payload: discord.RawReactionActionEvent
    ) -> None:
        guild = mongo.Guild(payload.guild_id)
        guild_info = await guild.check()

        emoji = guild_info.get('emoji', '')
        if emoji != str(payload.emoji):
            return

        receiver = await self.find_receiver(
            payload.channel_id, payload.message_id
        )

        if receiver == payload.user_id:
            pass

        user = mongo.User(receiver)

        guild_id = str(payload.guild_id)
        query = {f'economy.{guild_id}.balance': 1}
        await user.update(query, method='inc')


async def setup(bot: Bot) -> None:
    await bot.add_cog(Economy(bot))
