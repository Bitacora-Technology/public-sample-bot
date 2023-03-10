from discord.ext import commands
from discord import app_commands
from cogs.utils import mongo, format
from time import time
from bot import Bot
import discord


def giveaway_embed(giveaway_info: dict) -> discord.Embed:
    embed = discord.Embed(
        title=giveaway_info['name'], color=giveaway_info['color']
    )

    embed.set_footer(
        text='https://bitacora.gg', icon_url=giveaway_info['avatar']
    )

    user_list = giveaway_info.get('user_list', [])
    embed.add_field(name='Participants', value=len(user_list))

    winners = giveaway_info['winners']
    embed.add_field(name='Winners', value=winners)

    end_timestamp = giveaway_info['end']
    embed.add_field(name='Ends', value=f'<t:{end_timestamp}:R>')

    return embed


class ParticipateGroupbuyButton(discord.ui.Button):
    def __init__(self) -> None:
        super().__init__(
            label='Participate',
            style=discord.ButtonStyle.primary,
            custom_id='participate'
        )

    async def callback(self, interaction: discord.Interaction) -> None:
        giveaway = mongo.Giveaway(interaction.message.id)
        giveaway_info = await giveaway.check()

        if giveaway_info is None:
            content = 'Giveaway not found'
            await interaction.response.send_message(content, ephemeral=True)
            return

        user_id = interaction.user.id
        user_list = giveaway_info.get('user_list', [])

        if user_id not in user_list:
            user_list.append(user_id)
            action = 'joined'
        else:
            user_list.remove(user_id)
            action = 'left'

        await giveaway.update({'user_list': user_list})

        giveaway_info['user_list'] = user_list
        embed = giveaway_embed(giveaway_info)
        await interaction.message.edit(embed=embed)

        giveaway_name = giveaway_info['name']
        content = f'Giveaway \'{giveaway_name}\' {action}'
        await interaction.response.send_message(content, ephemeral=True)


class ParticipateGroupbuyView(discord.ui.View):
    def __init__(self) -> None:
        super().__init__(timeout=None)
        self.add_item(ParticipateGroupbuyButton())


class CreateGiveawayModal(discord.ui.Modal):
    def __init__(self, bot: Bot) -> None:
        super().__init__(title='Create giveaway')
        self.bot = bot
        self.time_table = {
            'w': 604800,
            'd': 86400,
            'h': 3600,
            'm': 60
        }

    name = discord.ui.TextInput(label='Name', max_length=256)

    winners = discord.ui.TextInput(label='Winners')

    end = discord.ui.TextInput(
        label='End',
        placeholder='1w: 1 week, 1d: 1 day, 1h: 1 hour, 1m: 1 minute'
    )

    def calculate_end(self) -> int:
        total_seconds = 0
        value_list = self.end.value.replace(',', '').split()
        for value in value_list:
            amount = int(value[:-1])
            unit = value[-1].lower()
            total_seconds += amount * self.time_table.get(unit, 0)
        return total_seconds

    async def on_submit(self, interaction: discord.Interaction) -> None:
        giveaway_end = self.calculate_end()
        if giveaway_end == 0:
            raise Exception('Giveaways end can\'t be 0')

        end_timestamp = int(time()) + giveaway_end

        giveaway_info = {
            'name': self.name.value,
            'winners': int(self.winners.value),
            'end': end_timestamp,
            'color': format.embed_color_dec,
            'avatar': format.bot_avatar_url
        }

        embed = giveaway_embed(giveaway_info)
        view = ParticipateGroupbuyView()
        message = await interaction.channel.send(embed=embed, view=view)
        giveaway_info['_id'] = message.id

        giveaway = mongo.Giveaway()
        await giveaway.create(giveaway_info)

        content = 'Giveaway has been created'
        await interaction.response.send_message(content, ephemeral=True)


@app_commands.guild_only()
@app_commands.default_permissions(administrator=True)
class Giveaways(commands.GroupCog, group_name='giveaways'):
    def __init__(self, bot: Bot) -> None:
        self.bot = bot

    @app_commands.command()
    async def create(self, interaction: discord.Interaction) -> None:
        """Create a new giveaway"""
        modal = CreateGiveawayModal(self.bot)
        await interaction.response.send_modal(modal)


async def setup(bot: Bot) -> None:
    await bot.add_cog(Giveaways(bot))
