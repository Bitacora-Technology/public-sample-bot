from discord.ext import commands
from discord import app_commands
from cogs.utils import mongo, embeds
from importlib import reload
from random import choices
from time import time
from bot import Bot
import discord
import asyncio


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

        title = giveaway_info['name']

        if giveaway_info is None:
            description = 'Giveaway not found'
            embed = embeds.simple_embed(title, description)
            await interaction.response.send_message(
                embed=embed, ephemeral=True
            )
            return

        user_id = interaction.user.id
        user_list = giveaway_info.get('user_list', [])

        if user_id not in user_list:
            user_list.append(user_id)
            description = 'Giveaway joined'
            await giveaway.update({'user_list': user_list})

            giveaway_info['user_list'] = user_list
            embed = embeds.giveaway_embed(giveaway_info)
            await interaction.message.edit(embed=embed)

        else:
            description = 'Giveaway already joined'

        embed = embeds.simple_embed(title, description)
        await interaction.response.send_message(embed=embed, ephemeral=True)


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

    async def finish_giveaway(self) -> None:
        giveaway = mongo.Giveaway(self.message.id)
        giveaway_info = await giveaway.check()

        name = giveaway_info['name']
        user_list = giveaway_info.get('user_list', [])
        winners = giveaway_info['winners']

        embed = embeds.giveaway_embed(giveaway_info)
        embed.remove_field(2)

        if winners > len(user_list):
            await self.message.edit(embed=embed)

            description = f'Not enough participants in \'{name}\' to draw a winner'
            embed = embeds.simple_embed(name, description)
            await self.message.reply(embed=embed)
            return

        winner_list = [f'<@{u}>' for u in choices(user_list, k=winners)]
        winner_text = ', '.join(winner_list)

        embed.remove_field(1)
        embed.add_field(name='Winners', value=winner_text)
        await self.message.edit(embed=embed, view=None)

        description = (
            f'Congratulations to {winner_text} for winning the giveaway'
        )
        embed = embeds.simple_embed(name, description)
        await self.message.reply(embed=embed)

        await giveaway.delete()

    async def on_submit(self, interaction: discord.Interaction) -> None:
        giveaway_end = self.calculate_end()
        if giveaway_end == 0:
            raise Exception('Giveaways end can\'t be 0')

        end_timestamp = int(time()) + giveaway_end

        giveaway_info = {
            'name': self.name.value,
            'winners': int(self.winners.value),
            'end': end_timestamp
        }

        embed = embeds.giveaway_embed(giveaway_info)
        view = ParticipateGroupbuyView()
        self.channel = interaction.channel
        self.message = await self.channel.send(embed=embed, view=view)
        giveaway_info['_id'] = self.message.id

        giveaway = mongo.Giveaway()
        await giveaway.create(giveaway_info)

        title = giveaway_info['name']
        description = 'Giveaway has been created'
        embed = embeds.simple_embed(title, description)
        await interaction.response.send_message(embed=embed, ephemeral=True)

        await asyncio.sleep(giveaway_end)
        await self.finish_giveaway()


@app_commands.guild_only()
@app_commands.default_permissions(administrator=True)
class Giveaways(commands.GroupCog, group_name='giveaways'):
    def __init__(self, bot: Bot) -> None:
        self.bot = bot

    async def cog_load(self) -> None:
        module_list = [mongo, embeds]
        for module in module_list:
            reload(module)

        view_list = [ParticipateGroupbuyView()]
        for view in view_list:
            self.bot.add_view(view)

    @app_commands.command()
    async def create(self, interaction: discord.Interaction) -> None:
        """Create a new giveaway"""
        modal = CreateGiveawayModal(self.bot)
        await interaction.response.send_modal(modal)


async def setup(bot: Bot) -> None:
    await bot.add_cog(Giveaways(bot))
