import discord
from discord.ext import commands, tasks
from utils.Music import Music
import asyncio
import json


class MusicControl(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.music = Music()
        self.config = None

    @commands.Cog.listener()
    async def on_message(self, message):
        data = await self.client.config.find(str(message.guild.id))
        language = data["language"]

        with open('config/language.json', 'r') as f:
            conf = json.load(f)
        self.config = conf[language]

    @commands.Cog.listener()
    async def on_voice_state_update(self, user, before, after):
        if after.channel is None and user.id == self.client.user.id:
            self.music = Music()
            self.checkPlaying.cancel()

    @commands.command()
    @commands.guild_only()
    async def join(self, ctx):
        authorvoice = ctx.author.voice
        if authorvoice is None:
            return await ctx.send(embed=discord.Embed(
                title="", description=self.config["notinvoice"]))
        await ctx.author.voice.channel.connect()
        await ctx.send(
            embed=discord.Embed(title="", description=self.config["join"]))
        await asyncio.sleep(120)
        self.checkPlaying.start(ctx)

    @commands.command()
    @commands.guild_only()
    async def leave(self, ctx):
        authorvoice = ctx.author.voice
        if authorvoice is None:
            return await ctx.send(embed=discord.Embed(
                title="", description=self.config["notinvoice"]))
        botvoice = ctx.guild.me.voice
        if botvoice is None:
            return await ctx.send(embed=discord.Embed(
                title="", description=self.config["leave_notinvoice"]))
        await ctx.voice_client.disconnect()
        await ctx.send(
            embed=discord.Embed(title="", description=self.config["leave"]))

    @commands.command(aliases=["p"])
    @commands.guild_only()
    async def play(self, ctx, *, url):
        authorvoice = ctx.author.voice
        botvoice = ctx.guild.me.voice
        if authorvoice is None:
            return await ctx.send(embed=discord.Embed(
                title="", description=self.config["notinvoice"]))
        if botvoice is None:
            await ctx.author.voice.channel.connect()

        player = self.music.get_player(guild_id=ctx.guild.id)
        if not player:
            player = self.music.create_player(ctx, ffmpeg_error_betterfix=True)
        if not ctx.voice_client.is_playing():
            await player.queue(url, bettersearch=True)
            song = await player.play()
            embed = discord.Embed(title=self.config["now_playing"],
                                  description=f"[{song.name}]({song.url})")
            await ctx.send(embed=embed)
        else:
            song = await player.queue(url, bettersearch=True)
            await ctx.send(embed=discord.Embed(
                title="",
                description=eval("f'{}'".format(self.config["queue_song"]))))
        self.checkPlaying.start(ctx)

    @commands.command()
    @commands.guild_only()
    async def pause(self, ctx):
        player = self.music.get_player(guild_id=ctx.guild.id)
        song = await player.pause()
        await ctx.send(embed=discord.Embed(
            title="", description=eval("f'{}'".format(self.config["pause"]))))

    @commands.command()
    @commands.guild_only()
    async def resume(self, ctx):
        player = self.music.get_player(guild_id=ctx.guild.id)
        song = await player.resume()
        await ctx.send(embed=discord.Embed(
            title="", description=eval("f'{}'".format(self.config["resume"]))))

    @commands.command(aliases=["q"])
    @commands.guild_only()
    async def queue(self, ctx):
        player = self.music.get_player(guild_id=ctx.guild.id)
        embed = discord.Embed(title=self.config["queue"], description="")
        order = 1
        for song in player.current_queue():
            embed.description += f"{order}, [{song.name}]({song.url})\n"
            order += 1
        embed.add_field(name='\u200b',
                        value=eval("f'{}'".format(self.config["queue_end"])))
        await ctx.send(embed=embed)

    @commands.command()
    @commands.guild_only()
    async def stop(self, ctx):
        player = self.music.get_player(guild_id=ctx.guild.id)
        await player.stop()
        await ctx.send(
            embed=discord.Embed(title="", description=self.config["stop"]))

    @commands.command(aliases=["np"])
    @commands.guild_only()
    async def nowplaying(self, ctx):
        player = self.music.get_player(guild_id=ctx.guild.id)
        song = player.now_playing()
        embed = discord.Embed(title=self.config["now_playing"],
                              description=f"[{song.name}]({song.url})")
        embed.set_thumbnail(url=song.thumbnail)
        embed.add_field(name=self.config["np_author"],
                        value=f"[{song.channel}]({song.channel_url})",
                        inline=True)
        embed.add_field(name=self.config["np_view"],
                        value=f'{song.views:,}',
                        inline=True)
        embed.add_field(
            name=self.config["np_duration"],
            value=f'{int(int(song.duration)/60)}:{int(song.duration)%60:02d}',
            inline=True)
        await ctx.send(embed=embed)

    @commands.command()
    @commands.guild_only()
    async def skip(self, ctx):
        player = self.music.get_player(guild_id=ctx.guild.id)
        data = await player.skip(force=True)
        await ctx.send(embed=discord.Embed(
            title="", description=eval("f'{}'".format(self.config["skip"]))))

    @commands.command()
    @commands.guild_only()
    async def volume(self, ctx, vol):
        player = self.music.get_player(guild_id=ctx.guild.id)
        song, volume = await player.change_volume(
            float(vol) / 100)  # volume should be a float between 0 to 1
        await ctx.send(embed=discord.Embed(
            title="", description=eval("f'{}'".format(self.config["volume"]))))

    @commands.command()
    @commands.guild_only()
    async def remove(self, ctx, index: int):
        player = self.music.get_player(guild_id=ctx.guild.id)
        song = await player.remove_from_queue(int(index - 1))
        await ctx.send(embed=discord.Embed(
            title="", description=eval("f'{}'".format(self.config["remove"]))))

    @commands.command()
    @commands.guild_only()
    async def loop(
        self,
        ctx,
    ):
        player = self.music.get_player(guild_id=ctx.guild.id)
        song = await player.toggle_song_loop()
        if song.is_looping:
            await ctx.send(embed=discord.Embed(title="",
                                               description=eval("f'{}'".format(
                                                   self.config["loop"]))))
        else:
          await ctx.send(embed=discord.Embed(title="",
                                               description=eval("f'{}'".format(
                                                   self.config["unloop"]))))

    @tasks.loop(seconds=10)
    async def checkPlaying(self, ctx):
        player = self.music.get_player(guild_id=ctx.guild.id)
        botvoice = ctx.guild.me.voice
        if botvoice is not None:
            if player is None or player is not None and player.now_playing(
            ) is None:
                await asyncio.sleep(300)
                if player is None or player is not None and player.now_playing(
                ) is None:
                    await ctx.voice_client.disconnect()
                    await ctx.send(embed=discord.Embed(
                        title="", description=self.config["auto_leave"]))

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.errors.NoPrivateMessage):
            await ctx.send(embed=discord.Embed(
                title="", description="You cannot send commands through DMs."))


def setup(client):
    client.add_cog(MusicControl(client))
