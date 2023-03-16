from discord.ext import commands
from discord import app_commands
from asyncio import TimeoutError
from cogs.utils import mongo, embeds
from importlib import reload
from bot import Bot
import discord


embed_title = '{}\'s economy'


class CheckBalanceButton(discord.ui.Button):
    def __init__(self) -> None:
        super().__init__(
            label='My balance',
            custom_id='check-balance',
            style=discord.ButtonStyle.primary
        )

    async def callback(self, interaction: discord.Interaction) -> None:
        user_id = interaction.user.id
        guild_id = interaction.guild_id

        guild_name = interaction.guild.name
        title = embed_title.format(guild_name)

        user = mongo.User(user_id)
        user_info = await user.check()

        economy_dict = user_info.get('economy', {})
        guild_economy = economy_dict.get(str(guild_id), {})
        balance = guild_economy.get('balance', 0)

        coin_text = 'coin'
        if balance != 1:
            coin_text += 's'

        description = f'Your balance is {balance} {coin_text}'
        embed = embeds.simple_embed(title, description)
        await interaction.response.send_message(embed=embed, ephemeral=True)


class GuildLeaderboardButton(discord.ui.Button):
    def __init__(self) -> None:
        super().__init__(
            label='Leaderboard',
            custom_id='guild-leaderboard',
            style=discord.ButtonStyle.primary
        )

    async def callback(self, interaction: discord.Interaction) -> None:
        guild_id = str(interaction.guild_id)
        users = mongo.User()
        cursor = users.cursor()

        user_list = []
        async for user_info in cursor:
            economy_info = user_info.get('economy', {})
            guild_economy = economy_info.get(guild_id, None)

            if guild_economy is None:
                continue

            user_item = {
                'id': user_info['_id'],
                'balance': guild_economy['balance']
            }
            user_list.append(user_item)

        guild_name = interaction.guild.name
        title = embed_title.format(guild_name)

        leaderboard = sorted(
            user_list, key=lambda u: u['balance'], reverse=True
        )[:10]

        description = ''
        for index in range(len(leaderboard)):
            user_id = leaderboard[index]['id']
            balance = leaderboard[index]['balance']

            coin_text = 'coin'
            if balance != 1:
                coin_text += 's'

            description += f'{index+1}. <@{user_id}>: {balance} {coin_text}\n'

        if description == '':
            description = 'No user has received any coin'

        embed = embeds.simple_embed(title, description)
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
        module_list = [mongo, embeds]
        for module in module_list:
            reload(module)

        view_list = [EconomyPanelView()]
        for view in view_list:
            self.bot.add_view(view)

    @app_commands.command()
    async def coin(self, interaction: discord.Interaction) -> None:
        """Set which emoji will act as coin"""
        await interaction.response.defer(ephemeral=True, thinking=True)

        guild_name = interaction.guild.name
        title = embed_title.format(guild_name)

        description = 'React with the emoji you want to use'
        embed = embeds.simple_embed(title, description)
        message = await interaction.channel.send(embed=embed)

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
            description = 'No reaction was received'
            embed = embeds.simple_embed(title, description)
            await interaction.followup.send(embed=embed)
            await message.delete()
            return

        emoji = str(reaction[0].emoji)
        await message.delete()

        guild = mongo.Guild(interaction.guild_id)
        await guild.update({'emoji': emoji})

        description = f'Emoji {emoji} has been set as coin'
        embed = embeds.simple_embed(title, description)
        await interaction.followup.send(embed=embed)

    @app_commands.command()
    async def panel(self, interaction: discord.Interaction) -> None:
        """Send an economy panel"""
        guild = mongo.Guild(interaction.guild_id)
        guild_info = await guild.check()

        guild_name = interaction.guild.name
        title = embed_title.format(guild_name)

        emoji = guild_info.get('emoji', None)
        if emoji is None:
            description = (
                'You need to set up the emoji that will act as a coin first'
            )
            embed = embeds.simple_embed(title, description)
            await interaction.response.send_message(
                embed=embed, ephemeral=True
            )
            return

        description = (
            'You can give a coin to an user reacting to his '
            f'message with emoji {emoji}'
        )
        embed = embeds.simple_embed(title, description)
        view = EconomyPanelView()
        await interaction.channel.send(embed=embed, view=view)

        description = 'Economy panel sent'
        embed = embeds.simple_embed(title, description)
        await interaction.response.send_message(embed=embed, ephemeral=True)

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

        emoji = guild_info.get('emoji', None)
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
