import discord


global_format = {
    'color': 12718096,
    'footer': 'https://bitacora.gg',
    'image': (
        'https://cdn.discordapp.com/avatars/1053306790026149978/'
        'e2aa0070242d8cfae68e6af0300e26e1.png'
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
