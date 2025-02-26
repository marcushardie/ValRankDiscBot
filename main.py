import os 
import sys
from dotenv import load_dotenv

import discord
from discord.ext import commands

from logs.log_settings import logger

from cogs.Admin import cogsControl_func, SyncSlashTree, AdminMessageConditions, helpFunction


#Load Token
load_dotenv()
TOKEN:str = os.getenv('DISCORD_TOKEN')
intents = discord.Intents.default()
intents.message_content = True

#Bot Setup
bot = commands.Bot(command_prefix ='!', help_command=None, intents=intents,case_insensitive=True)
#StartUp
@bot.event
async def on_ready():
    response = f'{bot.user} Started now running'
    logger.info(response)
    await cogsControl_func(bot, 'all', 'load')
    await SyncSlashTree(bot)


@bot.command(name= 'restart', description= 'Full Restart of the Program')
@commands.is_owner()
async def restart(ctx):
  if AdminMessageConditions(ctx):
    response:str = "Restarting"
    logger.info(response)
    await ctx.send("```" + response + "```" )
    os.execv(sys.executable, ['python'] + sys.argv)


#GlobalHelp command for all cogs
@bot.command(name="help", description="Returns all Admin Cog commands")
@commands.is_owner()
async def help(ctx):
    if AdminMessageConditions(ctx):
        msg:str = await helpFunction(bot)
        await ctx.send(msg)

#MAIN
if __name__ == "__main__":
 bot.run(token=TOKEN, root_logger=True)