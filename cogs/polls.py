from discord.ext import commands
from discord import app_commands
from cogs.utils import mongo, formatting
from bot import Bot
import discord


def calculate_total_votes(choice_list: list) -> int:
    votes = 0
    for choice in choice_list:
        votes += len(choice['votes'])
    return votes


def get_progress_bar(choice: int, total_votes: int) -> str:
    percentage = 100 * choice / total_votes
    full_count = int(percentage / 10)
    remainder = percentage % 10

    progress_bar = ''

    if full_count >= 1:
        emoji = ''
        progress_bar += emoji * full_count

    if remainder >= 7.5:
        emoji = ''
        progress_bar += emoji
    elif remainder >= 5:
        emoji = ''
        progress_bar += emoji
    elif remainder >= 2.5:
        emoji = ''
        progress_bar += emoji

    progress_bar += f' {round(percentage, 2)}%'
    return progress_bar


def poll_embed(poll_info) -> discord.Embed:
    embed = discord.Embed(
        title=poll_info['title'],
        color=formatting.embed_color_dec
    )

    embed.set_footer(
        text='https://bitacora.gg', icon_url=formatting.bot_avatar_url
    )

    choice_list = poll_info['choice_list']
    total_votes = calculate_total_votes(choice_list)

    count = 1
    for choice in choice_list:
        title = choice['title']
        if total_votes > 0:
            progress_bar = get_progress_bar(len(choice['votes']), total_votes)
        else:
            progress_bar = '0.0%'
        embed.add_field(
            name=f'{count}. {title}', value=progress_bar, inline=False
        )
        count += 1
    return embed


class CreatePollModal(discord.ui.Modal):
    def __init__(self) -> None:
        super().__init__(title='Create poll')

    _title = discord.ui.TextInput(label='Title', max_length=256)

    async def on_submit(self, interaction: discord.Interaction) -> None:
        poll_info = {
            'title': self._title.value,
            'choice_list': []
        }

        embed = poll_embed(poll_info)
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

        embed = poll_embed(self.poll_info)
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

        embed = poll_embed(self.poll_info)
        view = ConfigurePollView(self.poll_info)
        await interaction.response.edit_message(embed=embed, view=view)


class GoBackButton(discord.ui.Button):
    def __init__(self, poll_info: dict) -> None:
        super().__init__(label='Go back')
        self.poll_info = poll_info

    async def callback(self, interaction: discord.Interaction) -> None:
        embed = poll_embed(self.poll_info)
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
        embed = poll_embed(self.poll_info)
        view = RemoveChoiceView(self.poll_info)
        await interaction.response.edit_message(embed=embed, view=view)


class PublishPollButton(discord.ui.Button):
    def __init__(self, poll_info: dict, disabled: bool) -> None:
        super().__init__(
            label='Publish',
            style=discord.ButtonStyle.primary,
            disabled=disabled
        )
        self.poll_info = poll_info

    async def callback(self, interaction: discord.Interaction) -> None:
        pass


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

    @app_commands.command()
    async def create(self, interaction: discord.Interaction) -> None:
        """Create a new poll"""
        modal = CreatePollModal()
        await interaction.response.send_modal(modal)


async def setup(bot: Bot) -> None:
    await bot.add_cog(Polls(bot))
