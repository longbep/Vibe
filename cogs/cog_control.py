import discord
from discord.ext import commands


class CogControl(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command(hidden=True)
    @commands.is_owner()
    async def load(self, ctx, extension):
        self.client.load_extension(f'cogs.{extension}')
        await ctx.send("Load successful")

    @commands.command(hidden=True)
    @commands.is_owner()
    async def unload(self, ctx, extension):
        self.client.unload_extension(f'cogs.{extension}')
        await ctx.send("Unload successful")

    @commands.command(hidden=True)
    @commands.is_owner()
    async def reload(self, ctx, extension):
        self.client.reload_extension(f'cogs.{extension}')
        if ctx.guild.me.voice is not None:
            await ctx.voice_client.disconnect()
        await ctx.send("Reload successful")

    @commands.command(hidden=True)
    @commands.is_owner()
    async def status(self, ctx):
        totalMember = 0
        for guild in self.client.guilds:
            totalMember += guild.member_count

        await self.client.change_presence(activity=discord.Activity(
            name=
            f"-help | {len(self.client.guilds)} servers | {totalMember} members",
            type=discord.ActivityType.listening))
        await ctx.send("Reload status successful")


def setup(client):
    client.add_cog(CogControl(client))
