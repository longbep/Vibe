from discord.ext import commands
import os
from cogs.setting_control import CustomHelpCommand 
from keep_alive import keep_alive
import json

def get_prefix(client,message):
    with open('config/prefixes.json','r') as f:
      prefixes = json.load(f)
    return prefixes[str(message.guild.id)]

client = commands.Bot(command_prefix=get_prefix,help_command= CustomHelpCommand())

for filename in os.listdir('./cogs'):
  if(filename.endswith('.py') and filename != '__init__.py'):
    client.load_extension(f'cogs.{filename[:-3]}')

keep_alive()
client.run(os.getenv('TOKEN')) 