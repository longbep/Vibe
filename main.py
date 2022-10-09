import discord
from discord.ext import commands
import os
from cogs.setting_control import CustomHelpCommand
# from utils.keep_alive import keep_alive
# import json

import motor.motor_asyncio
from utils.mongo import Document


async def get_prefix(client, message):
    data = await client.config.find(str(message.guild.id))
    return data["prefix"]


client = commands.Bot(command_prefix=get_prefix,
                      help_command=CustomHelpCommand())


@client.event
async def on_ready():
    totalMember =0
    for guild in client.guilds:
      totalMember+=guild.member_count
      
    await client.change_presence(activity=discord.Activity(
        name=
        f"-help | {len(client.guilds)} servers | {totalMember} members",
        type=discord.ActivityType.listening))
    client.connection_url = os.getenv('MONGO')
    client.mongo = motor.motor_asyncio.AsyncIOMotorClient(
        str(client.connection_url))
    client.db = client.mongo['vibebot']
    client.config = Document(client.db, "config")


for filename in os.listdir('./cogs'):
    if (filename.endswith('.py') and filename != '__init__.py'):
        client.load_extension(f'cogs.{filename[:-3]}')

# keep_alive()
client.run(os.getenv('TOKEN'))
