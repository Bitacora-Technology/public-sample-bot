import discord


global_format = {
    'color': 12718096,
    'footer': 'https://bitacora.gg',
    'image': (
        'https://cdn.discordapp.com/avatars/1053306790026149978/'
        'e2aa0070242d8cfae68e6af0300e26e1.png'
    )
}

emoji_dict = {
    '100': '<:100percent:1085029281287110726>',
    '75': '<:75percent:1085029283480735825>',
    '50': '<:50percent:1085029285460443228>',
    '25': '<:25percent:1085029287754743878>'
}

help_dict = {
    'Economy': (
        'You can create an economy system in the community based in '
        'message reactions'
    ),
    'Embeds': (
        'You can send custom embeds easily with the integrated menu'
    ),
    'Giveaways': (
        'You can create giveaways to give back to your community in a '
        'randomized way'
    ),
    'Polls': (
        'You can create polls to collect users feedback or make decisions'
    ),
    'Tickets': (
        'You can send a panel where users can open private tickets to contact '
        'with staff for help or support'
    ),
    'Welcome': (
        'You can enable or disable receiving a notification in the selected '
        'channel when someone joins the server'
    )
}


def simple_embed(title: str, description: str) -> discord.Embed:
    embed = discord.Embed(
        title=title, description=description, color=global_format['color']
    )
    embed.set_footer(
        text=global_format['footer'], icon_url=global_format['image']
    )
    return embed


def advanced_embed(embed_info: dict) -> discord.Embed:
    embed = simple_embed(embed_info['title'], embed_info['description'])

    embed.set_image(url=embed_info['image_url'])
    embed.set_thumbnail(url=embed_info['thumbnail_url'])

    field_list = embed_info['field_list']
    for field in field_list:
        embed.add_field(name=field['name'], value=field['value'], inline=False)

    return embed


def giveaway_embed(giveaway_info: dict) -> discord.Embed:
    embed = simple_embed(giveaway_info['name'], None)

    user_list = giveaway_info.get('user_list', [])
    embed.add_field(name='Participants', value=len(user_list))

    winners = giveaway_info['winners']
    embed.add_field(name='Winners', value=winners)

    timestamp = giveaway_info['end']
    embed.add_field(name='Ends', value=f'<t:{timestamp}:R>')

    return embed


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
        emoji = emoji_dict['100']
        progress_bar += emoji * full_count

    if remainder >= 7.5:
        emoji = emoji_dict['75']
        progress_bar += emoji
    elif remainder >= 5:
        emoji = emoji_dict['50']
        progress_bar += emoji
    elif remainder >= 2.5:
        emoji = emoji_dict['25']
        progress_bar += emoji

    progress_bar += f' {round(percentage, 2)}%'
    return progress_bar


def poll_embed(poll_info: dict) -> discord.Embed:
    embed = simple_embed(poll_info['title'], None)

    choice_list = poll_info['choice_list']
    total_votes = calculate_total_votes(choice_list)

    count = 1
    for choice in choice_list:
        title = choice['title']
        votes = len(choice['votes'])

        if total_votes > 0:
            progress_bar = get_progress_bar(votes, total_votes)
        else:
            progress_bar = '0.0%'

        embed.add_field(name=title, value=progress_bar, inline=False)
        count += 1

    return embed


def help_embed() -> discord.Embed:
    embed = simple_embed('Bitacora help', None)

    for name, value in help_dict.items():
        embed.add_field(name=name, value=value, inline=False)

    return embed


def welcome_embed(member: discord.Member) -> discord.Embed:
    embed = simple_embed('New arrival', None)

    user_name = f'{member.name}#{member.discriminator}'
    embed.add_field(name='Member', value=user_name)

    embed.set_thumbnail(url=member.avatar)

    return embed
