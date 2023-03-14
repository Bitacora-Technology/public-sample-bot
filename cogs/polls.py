from discord.ext import commands
from discord import app_commands
from cogs.utils import mongo, embeds
from importlib import reload
from bot import Bot
import discord


class CreatePollModal(discord.ui.Modal):
    def __init__(self) -> None:
        super().__init__(title='Create poll')

    _title = discord.ui.TextInput(label='Title', max_length=256)

    async def on_submit(self, interaction: discord.Interaction) -> None:
        poll_info = {
            'title': self._title.value,
            'choice_list': []
        }

        embed = embeds.poll_embed(poll_info)
        view = ConfigurePollView(poll_info)
        await interaction.response.send_message(
            embed=embed, view=view, ephemeral=True
        )


class AddChoiceModal(discord.ui.Modal):
    def __init__(self, poll_info: dict) -> None:
        super().__init__(title='Add choice')
        self.poll_info = poll_info

    _title = discord.ui.TextInput(label='Title', max_length=256)

    async def on_submit(self, interaction: discord.Interaction) -> None:
        self.poll_info['choice_list'].append(
            {'title': self._title.value, 'votes': []}
        )

        embed = embeds.poll_embed(self.poll_info)
        view = ConfigurePollView(self.poll_info)
        await interaction.response.edit_message(embed=embed, view=view)


class AddChoiceButton(discord.ui.Button):
    def __init__(self, poll_info: dict, disabled: bool) -> None:
        super().__init__(label='Add choice', style=discord.ButtonStyle.success)
        self.poll_info = poll_info

    async def callback(self, interaction: discord.Interaction) -> None:
        modal = AddChoiceModal(self.poll_info)
        await interaction.response.send_modal(modal)


class RemoveButtonDropdown(discord.ui.Select):
    def __init__(self, poll_info: dict) -> None:
        options = []
        choice_list = poll_info['choice_list']
        count = 0
        for choice in choice_list:
            options.append(
                discord.SelectOption(
                    label=choice['title'][:100], value=str(count)
                )
            )
            count += 1
        super().__init__(
            placeholder='Choose the choices to remove...',
            min_values=1,
            max_values=len(choice_list),
            options=options
        )
        self.poll_info = poll_info

    async def callback(self, interaction: discord.Interaction) -> None:
        self.values.sort()
        self.values.reverse()
        for value in self.values:
            self.poll_info['choice_list'].pop(int(value))

        embed = embeds.poll_embed(self.poll_info)
        view = ConfigurePollView(self.poll_info)
        await interaction.response.edit_message(embed=embed, view=view)


class GoBackButton(discord.ui.Button):
    def __init__(self, poll_info: dict) -> None:
        super().__init__(label='Go back')
        self.poll_info = poll_info

    async def callback(self, interaction: discord.Interaction) -> None:
        embed = embeds.poll_embed(self.poll_info)
        view = ConfigurePollView(self.poll_info)
        await interaction.response.edit_message(embed=embed, view=view)


class RemoveChoiceView(discord.ui.View):
    def __init__(self, poll_info: dict) -> None:
        super().__init__(timeout=None)
        self.add_item(RemoveButtonDropdown(poll_info))
        self.add_item(GoBackButton(poll_info))


class RemoveChoiceButton(discord.ui.Button):
    def __init__(self, poll_info: dict, disabled: bool) -> None:
        super().__init__(
            label='Remove choice',
            style=discord.ButtonStyle.danger,
            disabled=disabled
        )
        self.poll_info = poll_info

    async def callback(self, interaction: discord.Interaction) -> None:
        embed = embeds.poll_embed(self.poll_info)
        view = RemoveChoiceView(self.poll_info)
        await interaction.response.edit_message(embed=embed, view=view)


class VotePollButton(discord.ui.Button):
    def __init__(self, count: int) -> None:
        super().__init__(label=str(count), style=discord.ButtonStyle.primary)

    async def callback(self, interaction: discord.Interaction) -> None:
        poll = mongo.Poll(interaction.message.id)
        poll_info = await poll.check()

        title = poll_info['title']
        user_id = interaction.user.id

        user_list = []
        choice_list = poll_info['choice_list']
        for choice in choice_list:
            [user_list.append(user) for user in choice['votes']]

        if user_id in user_list:
            description = 'You have already voted'
            embed = embeds.simple_embed(title, description)
            await interaction.response.send_message(
                embed=embed, ephemeral=True
            )
            return

        choice_list[int(self.label) - 1]['votes'].append(user_id)
        await poll.update({'choice_list': choice_list})

        embed = embeds.poll_embed(poll_info)
        await interaction.message.edit(embed=embed)

        description = 'Your vote has been registered'
        embed = embeds.simple_embed(title, description)
        await interaction.response.send_message(embed=embed, ephemeral=True)


class VotePollView(discord.ui.View):
    def __init__(self, choice_list: list) -> None:
        super().__init__(timeout=None)
        for count in range(1, len(choice_list) + 1):
            self.add_item(VotePollButton(count))


class PublishPollButton(discord.ui.Button):
    def __init__(self, poll_info: dict, disabled: bool) -> None:
        super().__init__(
            label='Publish',
            style=discord.ButtonStyle.primary,
            disabled=disabled
        )
        self.poll_info = poll_info

    async def callback(self, interaction: discord.Interaction) -> None:
        embed = embeds.poll_embed(self.poll_info)
        view = VotePollView(self.poll_info['choice_list'])
        message = await interaction.channel.send(embed=embed, view=view)
        self.poll_info['_id'] = message.id

        poll = mongo.Poll()
        await poll.create(self.poll_info)

        title = self.poll_info['title']
        description = 'Poll has been created'
        embed = embeds.simple_embed(title, description)
        await interaction.response.send_message(embed=embed, ephemeral=True)


class ConfigurePollView(discord.ui.View):
    def __init__(self, poll_info: dict) -> None:
        super().__init__(timeout=None)
        choice_list = poll_info['choice_list']
        self.add_item(AddChoiceButton(poll_info, len(choice_list) == 25))
        self.add_item(RemoveChoiceButton(poll_info, len(choice_list) == 0))
        self.add_item(PublishPollButton(poll_info, len(choice_list) < 2))


@app_commands.guild_only()
@app_commands.default_permissions(administrator=True)
class Polls(commands.GroupCog, group_name='polls'):
    def __init__(self, bot: Bot) -> None:
        self.bot = bot

    async def cog_load(self) -> None:
        module_list = [mongo, embeds]
        for module in module_list:
            reload(module)

    @app_commands.command()
    async def create(self, interaction: discord.Interaction) -> None:
        """Create a new poll"""
        modal = CreatePollModal()
        await interaction.response.send_modal(modal)


async def setup(bot: Bot) -> None:
    await bot.add_cog(Polls(bot))
