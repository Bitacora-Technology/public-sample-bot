from discord.ext import commands, tasks
from cogs.utils import embeds
from importlib import reload
from bot import Bot
import logging
import discord

log = logging.getLogger(__name__)


class Owner(commands.Cog):
    def __init__(self, bot: Bot) -> None:
        self.bot = bot
        self.delay = 10  # Seconds to wait to delete a message
        self.channel_id = 1085391909763158086

    async def cog_load(self) -> None:
        module_list = [embeds]
        for module in module_list:
            reload(module)

        self.update_presence.start()

    async def cog_unload(self) -> None:
        if self.update_presence.is_running() is True:
            self.update_presence.cancel()

    async def cog_check(self, ctx: commands.Context) -> bool:
        return await self.bot.is_owner(ctx.author)

    @commands.command()
    async def stats(self, ctx: commands.Context) -> None:
        """Get the bot stats"""
        member_count = 0
        guild_list = self.bot.guilds
        for guild in guild_list:
            member_count += guild.member_count

        content = f'{member_count} members from {len(guild_list)} guilds'
        await ctx.send(content, delete_after=self.delay)

    @commands.command()
    async def cogs(self, ctx: commands.Context) -> None:
        """Get the cog list"""
        cog_list = self.bot.cogs
        content = '\n'.join(cog_list)
        await ctx.send(content, delete_after=self.delay)
        await ctx.message.delete(delay=self.delay)

    @commands.command()
    async def update(self, ctx: commands.Context) -> None:
        """Reload all extensions"""
        cog_list = [c for c in self.bot.cogs]
        for cog in cog_list:
            extension = cog.lower()
            try:
                await self.bot.reload_extension(f'cogs.{extension}')
            except Exception as e:
                await ctx.send(
                    f'{e.__class__.__name__}: {e}',
                    delete_after=self.delay
                )
                log.exception(f'Failed to reload extension {extension}')
            else:
                await ctx.send(
                    f'Extension \'{extension}\' reloaded.',
                    delete_after=self.delay
                )
                log.info(f'Successfully reloaded extension {extension}')
        await ctx.message.delete(delay=self.delay)

    @commands.command()
    async def load(self, ctx: commands.Context, extension: str) -> None:
        """Loads a extension"""
        try:
            await self.bot.load_extension(f'cogs.{extension}')
        except commands.ExtensionError as e:
            await ctx.send(
                f'{e.__class__.__name__}: {e}',
                delete_after=self.delay
            )
            log.exception(f'Failed to load extension {extension}')
        else:
            await ctx.send(
                f'Extension \'{extension}\' loaded.',
                delete_after=self.delay
            )
            log.info(f'Successfully loaded extension {extension}')
        await ctx.message.delete(delay=self.delay)

    @commands.command()
    async def unload(self, ctx: commands.Context, extension: str) -> None:
        """Unloads a extension"""
        try:
            await self.bot.unload_extension(f'cogs.{extension}')
        except commands.ExtensionError as e:
            await ctx.send(
                f'{e.__class__.__name__}: {e}',
                delete_after=self.delay
            )
            log.exception(f'Failed to unload extension {extension}')
        else:
            await ctx.send(
                f'Extension \'{extension}\' unloaded.',
                delete_after=self.delay
            )
            log.info(f'Successfully unloaded extension {extension}')
        await ctx.message.delete(delay=self.delay)

    @commands.command()
    async def reload(self, ctx: commands.Context, extension: str) -> None:
        """Reloads a extension"""
        try:
            await self.bot.reload_extension(f'cogs.{extension}')
        except commands.ExtensionError as e:
            await ctx.send(
                f'{e.__class__.__name__}: {e}',
                delete_after=self.delay
            )
            log.exception(f'Failed to reload extension {extension}')
        else:
            await ctx.send(
                f'Extension \'{extension}\' reloaded.',
                delete_after=self.delay
            )
            log.info(f'Successfully reloaded extension {extension}')
        await ctx.message.delete(delay=self.delay)

    @commands.command()
    async def sync(self, ctx: commands.Context, target: str = '') -> None:
        """Syncs the slash commands"""
        if target == 'global':
            guild = None
        elif target == 'guild':
            guild = ctx.guild
            self.bot.tree.copy_global_to(guild=guild)
        else:
            return await ctx.send(
                'You need to specify the sync target',
                delete_after=self.delay
            )

        commands_sync = await self.bot.tree.sync(guild=guild)
        await ctx.send(
            f'Successfully synced {len(commands_sync)} commands',
            delete_after=self.delay
        )
        log.info(f'Successfully synced {len(commands_sync)} commands')
        await ctx.message.delete(delay=self.delay)

    @commands.command()
    async def clear(self, ctx: commands.Context, target: str = '') -> None:
        """Clears the slash commands"""
        if target == 'global':
            guild = None
        elif target == 'guild':
            guild = ctx.guild
            self.bot.tree.copy_global_to(guild=guild)
        else:
            return await ctx.send(
                'You need to specify the clear target',
                delete_after=self.delay
            )

        self.bot.tree.clear_commands(guild=guild)
        await self.bot.tree.sync(guild=guild)
        await ctx.send(
            'Successfully cleared commands',
            delete_after=self.delay
        )
        log.info('Successfully cleared commands')
        await ctx.message.delete(delay=self.delay)

    @commands.Cog.listener()
    async def on_guild_join(self, guild: discord.Guild) -> None:
        channel = self.bot.get_channel(self.channel_id)
        if channel is None:
            channel = await self.bot.fetch_channel(self.channel_id)

        embed = embeds.guild_embed(guild)
        await channel.send(embed=embed)

    @tasks.loop(hours=12)
    async def update_presence(self) -> None:
        await self.bot.wait_until_ready()

        guild_list = self.bot.guilds
        name = f'{len(guild_list)} servers'
        watching = discord.ActivityType.watching
        activity = discord.Activity(type=watching, name=name)
        await self.bot.change_presence(activity=activity)


async def setup(bot: Bot) -> None:
    await bot.add_cog(Owner(bot))
