from discord.ext import commands
import json
import discord

class SettingControl(commands.Cog):

  def __init__(self,client):
    self.client = client
    self.config = None

  @commands.Cog.listener()
  async def on_message(self,message):
    data = await self.client.config.find(str(message.guild.id))
    language =  data["language"]

    with open('config/language.json','r') as f:
      conf = json.load(f)
    self.config = conf[language]

  @commands.Cog.listener()
  async def on_guild_join(self,guild):
    await self.client.config.insert({"_id": str(guild.id),"name": str(guild.name), "prefix": "-","language":"eng"})

  @commands.Cog.listener()
  async def on_guild_remove(self,guild):
    await self.client.config.delete(str(guild.id))

  @commands.command()
  @commands.guild_only()
  async def prefix(self,ctx,pre):
    await self.client.config.upsert({"_id": str(ctx.guild.id), "prefix": pre})

    await ctx.send(embed=discord.Embed(title="",description=eval("f'{}'".format(self.config["prefix"]))))

  @commands.command(aliases=["lang"])
  @commands.guild_only()
  async def language(self,ctx,language):
    await self.client.config.upsert({"_id": str(ctx.guild.id), "language": language})
    with open('config/language.json','r') as f:
      conf = json.load(f)
    self.config = conf[language]

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
    self.config=None
    self.prefix=None
  
  async def send_bot_help(self,mapping):
    if self.context.guild is None:
      language = "eng"
      self.prefix = "-"
    else:
      data = await self.context.bot.config.find(str(self.context.guild.id))
      language =  data["language"]
      self.prefix = data["prefix"]

    with open('config/language.json','r') as f:
      conf = json.load(f)
    self.config = conf[language]

    embed = discord.Embed(description=self.config["help_description"])
    
    embed.set_author(name = self.context.bot.user.name, icon_url = self.context.bot.user.avatar_url)
    embed.add_field(name=self.config["command"],value="\u200b",inline=False)
    for cog in mapping:
      if cog!=None:
        if cog.qualified_name != "CogControl":
          for command in mapping[cog]:
            embed.add_field(name=f"`{self.prefix}{command.name}`",value=self.config[command.name+"_brief"]+str(command.aliases),inline=True)

    embed.add_field(name=self.config["invite_name"],value=self.config["invite_value"],inline=False)
    embed.set_footer(text=eval("f'{}'".format(self.config["help_footer"])))
    await self.get_destination().send(embed=embed)

  async def send_command_help(self,command):
    if self.context.guild is None:
      language = "eng"
      self.prefix = "-"
    else:
      data = await self.context.bot.config.find(str(self.context.guild.id))
      language =  data["language"]
      self.prefix = data["prefix"]

    with open('config/language.json','r') as f:
      conf = json.load(f)
    self.config = conf[language]
    
    embed = discord.Embed(title=f"**{self.prefix}{command.name}**")
    embed.add_field(name=eval("f'{}'".format(self.config["help_command"])),value =self.config[command.name+"_help"])
    await self.get_destination().send(embed=embed)