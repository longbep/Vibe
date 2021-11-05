from discord.ext import commands
import json
import discord

class SettingControl(commands.Cog):

  def __init__(self,client):
    self.client = client
    self.config = None

  @commands.Cog.listener()
  async def on_message(self,message):
    with open('config/server_language.json','r') as f:
      lang = json.load(f)
    language =  lang[str(message.guild.id)]

    with open('config/language.json','r') as f:
      conf = json.load(f)
    self.config = conf[language]

  @commands.Cog.listener()
  async def on_guild_join(self,guild):
    with open('config/prefixes.json','r') as f:
      prefixes = json.load(f)
    prefixes[str(guild.id)]='-'
    with open('config/prefixes.json','w') as f:
      json.dump(prefixes,f,indent = 4)

    with open('config/server_language.json','r') as f:
      lang = json.load(f)
    lang[str(guild.id)]='eng'
    with open('config/server_language.json','w') as f:
      json.dump(lang,f,indent = 4)  

  @commands.Cog.listener()
  async def on_guild_remove(self,guild):
    with open('config/prefixes.json','r') as f:
      prefixes = json.load(f)
    prefixes.pop(str(guild.id))
    with open('config/prefixes.json','w') as f:
      json.dump(prefixes,f,indent = 4)

    with open('config/server_language.json','r') as f:
      lang = json.load(f)
    lang.pop(str(guild.id))
    with open('config/server_language.json','w') as f:
      json.dump(lang,f,indent = 4)  

  @commands.command(brief = "Change server prefix.", help = "prefix [prefix]\nChange server prefix.")
  @commands.guild_only()
  async def prefix(self,ctx,pre):
    with open('config/prefixes.json','r') as f:
      prefixes = json.load(f)

    prefixes[str(ctx.guild.id)]=pre

    with open('config/prefixes.json','w') as f:
      json.dump(prefixes,f,indent = 4)
    await ctx.send(embed=discord.Embed(title="",description=eval("f'{}'".format(self.config["prefix"]))))

  @commands.command(aliases=["lang"],brief = "Change server language.", help = "language / lang [eng/vie]\nChange server language (English, Tiếng Việt).")
  @commands.guild_only()
  async def language(self,ctx,language):
    with open('config/server_language.json','r') as f:
      lang = json.load(f)

    lang[str(ctx.guild.id)]=language
    lng = lang["lang"][language]

    with open('config/server_language.json','w') as f:
      json.dump(lang,f,indent = 4)
    await ctx.send(embed=discord.Embed(title="",description=eval("f'{}'".format(self.config["language"]))))

  @commands.Cog.listener()
  async def on_command_error(self,ctx, error):
    if isinstance(error, commands.errors.NoPrivateMessage):
      await ctx.send(embed=discord.Embed(title="",description="You cannot send commands through DMs."))
    
def setup(client):
  client.add_cog(SettingControl(client))

class CustomHelpCommand(commands.HelpCommand):
  def __init__(self):
    super().__init__()
  
  async def send_bot_help(self,mapping):
    embed = discord.Embed()
    
    embed.set_author(name = self.context.bot.user.name, icon_url = self.context.bot.user.avatar_url)
    await self.get_destination().send(embed=embed)

  # async def send_command_help(self,command):