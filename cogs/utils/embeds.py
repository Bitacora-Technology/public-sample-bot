import discord


embed_info = {
    'color': 12718096,
    'footer': 'https://bitacora.gg',
    'image': (
        'https://cdn.discordapp.com/avatars/1053306790026149978/'
        'e2aa0070242d8cfae68e6af0300e26e1.png'
    )
}


def simple_embed(title: str, description: str) -> discord.Embed:
    embed = discord.Embed(
        title=title, description=description, color=embed_info['color']
    )
    embed.set_footer(text=embed_info['footer'], icon_url=embed_info['image'])
    return embed
