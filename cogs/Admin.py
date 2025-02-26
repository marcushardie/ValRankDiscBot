import os
import json

import discord
from discord.ext import commands
from logs.log_settings import logger
from discord import app_commands

authorID = 172616667308883968

def AdminMessageConditions(ctx) -> bool:
    return (ctx.channel.type[0] == 'private') & (ctx.message.author.id == authorID)

def AdminMessageConditions_Slash(interaction: discord.Interaction) -> bool:
    return (interaction.channel.type.name == 'private') & (interaction.user.id == authorID)

async def helpFunction(bot) -> str:       
    response = []

    for command in bot.commands:
        if not command.name == "help":

            cCog:str  = "None"
            cName:str = "None"

            if not command.cog_name  ==  None : cCog    = command.cog_name
            if not command.name      ==  None : cName   = command.name
            
            cParm:str = ""
            for com in command.params:
                cParm+= ", " + str(command.params[com])
            
            cParm:str   = cParm[2:]
            cDes:str    = command.description
            if cParm == "": cParm = "None"
            if cDes  == "": cDes  = "None"
            
            helptext = "```"
            helptext+= f"    Cog : {cCog} \n   Name : {cName} \n Param. : {cParm} \n  Desc. : {cDes}"
            helptext+= "```"
            response.append(helptext)
        
    response.sort()
    response.insert(0,"```!help : \nAll Bot Commands :```")
    response = ''.join(response)
    return response

#Load , Unlaod , Reloader
async def cogsControl_func(self,cogFile_inpt:str,oad:str) -> str:
    oad = oad.lower()
    cogs = []
    cogFile_inpt = cogFile_inpt.title()
    ljsut_oded:int = 10
    msg:str ="" 

    if oad == 'load' or oad == 'unload' or oad == 'reload':
        #for all files
        if cogFile_inpt.lower() == 'all':
            for filename in os.listdir('./cogs'):
                if filename.endswith('.py'):
                    cogPath =  f'cogs.{filename[:-3]}' 
                    if cogPath == __name__ and oad == 'unload':
                       msg = f'cogs {(oad+"ed").ljust(ljsut_oded)} : SKIPPED : admin cannot be unloaded: {cogPath}, '
                       pass
                    else:
                       cogs.append(cogPath)
        else:
            cogs.append(f'cogs.{cogFile_inpt}')
        
        
        for cogPath in cogs:
            if oad == 'reload':
                try:
                    await self.reload_extension(cogPath)
                    msg+= (f'{cogPath}, ')
                except commands.ExtensionNotLoaded:
                    msg+= (f'[SKIPPED : as not loaded: {cogPath}], ')
                    pass

            elif oad == 'unload':
                if cogPath == __name__ and oad == 'unload':
                    msg+= (f'[SKIPPED : admin cannot be unloaded: {cogPath}], ')
                    pass
                else:
                    try:
                        await self.unload_extension(cogPath)
                        msg+= f'{cogPath}, '
                        
                    except commands.ExtensionNotFound:
                        msg+= f'[SKIPPED : extention not found : {cogPath}], '
                    
                    except commands.ExtensionNotLoaded:
                        msg+= f'[SKIPPED : not loaded : {cogPath}], '
                    
                
            elif oad == 'load': 
                try:
                    await self.load_extension(cogPath)
                    msg+= f'{cogPath}, '

                except commands.ExtensionAlreadyLoaded:
                    msg+= f'[SKIPPED : already loaded : {cogPath}], '
        
        msg = f"cog {oad}ed : {msg[:-2]}"
        logger.info(msg)
    else:
       msg="Bad_oad [" + oad + "]"
       logger.error(msg) 
    
    msg = "\n```\n" + msg + "\n```" 
    return msg

#Shows each cogs status
async def ShowCogs_embed(self):

    cogs_loaded:str     = ''
    cogs_unloaded:str   = ''
    cogs_NotFound:str   = ''

    for filename in os.listdir('cogs'):
        
        if filename.endswith('.py'):
            filename = filename[:-3]
            
            try:
                await self.load_extension(f"cogs.{filename}")
                
            except commands.ExtensionAlreadyLoaded:
                cogs_loaded = cogs_loaded + '\n' + filename
                
            except commands.ExtensionNotFound:
                cogs_NotFound = cogs_NotFound + '\n' + filename
            
            else:
                await self.unload_extension(f"cogs.{filename}")
                cogs_unloaded = cogs_unloaded + '\n' + filename
                
    embed = discord.Embed(title='All Cogs', description="saved under /cogs",  color=discord.Color.dark_gray())  
    if not cogs_loaded      == '': embed.add_field(name="Loaded",   value=cogs_loaded,   inline=False)
    if not cogs_unloaded    == '': embed.add_field(name="Unloaded", value=cogs_unloaded, inline=False)
    if not cogs_NotFound    == '': embed.add_field(name="Not Found",value=cogs_NotFound, inline=False)

    return embed


async def ShowCogs_text(self):

    cogs_loaded:str     = ''
    cogs_unloaded:str   = ''
    cogs_NotFound:str   = ''

    for filename in os.listdir('cogs'):
        
        if filename.endswith('.py'):
            filename = filename[:-3]
            
            try:
                await self.load_extension(f"cogs.{filename}")
                
            except commands.ExtensionAlreadyLoaded:
                cogs_loaded = cogs_loaded + '\n  ' + filename

            except commands.ExtensionNotFound:
                cogs_NotFound = cogs_NotFound + '\n  ' + filename

            else:
                await self.unload_extension(f"cogs.{filename}")
                cogs_unloaded = cogs_unloaded + '\n  ' + filename
                
    header = "All Cogs saved under /cogs : "
    response = ""
    if not cogs_loaded      == '': response+=f"\nLoaded: {cogs_loaded}"
    if not cogs_unloaded    == '': response+=f"\n\nUnloaded: {cogs_unloaded}"
    if not cogs_NotFound    == '': response+=f"\n\nNot Found: {cogs_NotFound}"
    
    if response == '': response = "None"
    response = f'```{header}{response}```'
    return response



async def SyncSlashTree(self, ctx=None):
    #Sync slash tree for updating name/desc. data for slash commands
    try:
        synced = await self.tree.sync()
        msg = f"synced {len(synced)} slash commands(s)"
        logger.info(msg)
        
    except Exception as e:
        msg = f'Slash command Tree error : {e}'
        logger.error(msg)
    
    if not ctx == None: await ctx.send(f'```{msg}```')


class admin(commands.Cog):
    def __init__(self,bot):
        self.bot = bot   

    @commands.Cog.listener()
    #only raises on command not found error
    async def on_command_error(self, ctx, error):
        if AdminMessageConditions(ctx):
            if isinstance(error, commands.CommandNotFound):
                response = f"{error} - use !help to get list of commands"
                await ctx.send(response)
                logger.info(response)
                return
            raise error


    @commands.command(name="cogs",description="show all cogs")
    @commands.is_owner()
    async def cogs(self, ctx):
        if AdminMessageConditions(ctx):
            res = await ShowCogs_text(self.bot)
            await ctx.send(res)
            #await ctx.send(embed=await ShowCogs_embed(self.bot))
    

    @commands.command(name="cc",description="cogs nanme then action of load/unload/reload")
    @commands.is_owner()
    async def cogsControl(self, ctx, cogfile:str = "all", action:str = "reload"):
        if AdminMessageConditions(ctx):
            content = (await cogsControl_func(self.bot,cogfile,action))
            await ctx.send(content=content)


    @commands.command(name="sst",description="Sync the slash tree")
    @commands.is_owner()
    async def SlashTree_sst(self, ctx):
        if AdminMessageConditions(ctx):
            await SyncSlashTree(self.bot, ctx)
            
    
    @app_commands.command(name = 'feature_suggestion', description = 'Provide suggestions for features to be added')
    async def AddPlayer_Blank(self,interaction: discord.Interaction, suggestion:str):    
        
        with open('data/feature_responses_sugg.json','r') as json_file:
            suggestion_dic  = json.load(json_file)
        
        suggestion_dic.append(suggestion)
    
        with open('data/feature_responses_sugg.json','w') as json_file:
            json.dump(suggestion_dic,json_file,indent=4)
            
        await interaction.response.send_message(content = f'Suggested : {suggestion}', ephemeral=True)
            

async def setup(bot):
    await bot.add_cog(admin(bot))
