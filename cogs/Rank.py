import asyncio
import json
import random
from datetime import datetime

import discord
from discord.ext import commands
from discord import app_commands


from logs.log_settings import logger
from cogs.Admin import AdminMessageConditions,AdminMessageConditions_Slash

from Val_Rank_API import ValRank_API_update


#DATA - FileLocations
RanksPlayerRanks_json:str = 'data/PlayerRanks.json'
RanksAPI_Folder:str = 'data/Rank_valorantApi'
RanksPhraseResponse_json:str = 'data/PhraseResponse/phrase_reponses.json'
RanksPhraseResponse_sug_json:str = 'data/PhraseResponse/phrase_responses_sugg.json'
RanksEmojis_json:str ='data/rank_emoji_ids.json'


#Format
date_timeFormat = "%y-%m-%d _ %H-%M-%S"
    
#FUNCTIONS
def PlayerRanksDict() -> dict:
    with open(RanksPlayerRanks_json,'r') as json_file:
            playerRanks = json.load(json_file)
    return playerRanks

def Latest_Timestamp(PlayerRanks) -> str:
    times = []
    for p in PlayerRanks:
        time = PlayerRanks[p]['DateOfRank']
        times.append(time)
    times.sort(reverse=True)
    lastTime = times[0]

    timestamp = datetime.strptime(lastTime,date_timeFormat)
    timestamp = timestamp.strftime("%d-%b-%y @ %I:%M %p")
    return timestamp


def UpdateRanks_function(playerName_list:list) -> str:
    logger.info(f"UPDATE RANKS : -- RUN --")

    #load neeced dics from JSONS
    with open(RanksPlayerRanks_json) as json_file:
        PlayerRanks = dict(json.load(json_file))
        
    with open(RanksEmojis_json) as json_file:
        rank_emoji_dic = json.load(json_file)

    with open(RanksPhraseResponse_json) as json_file:
        rank_key_phrase = json.load(json_file)

    response = []
    
    magnitude:int = 0
    for p in playerName_list:   
        try:
            with open(f'{RanksAPI_Folder}/{p}.json') as json_file:
                Ranks = json.load(json_file)
            
            magnitude = 0

            #Double check status res for error / other event handle
            if (Ranks['status']==200) & ((Ranks['data']['account']['name'] + '#' + Ranks['data']['account']['tag']).lower() == (p)): 
                
                PlayerRank_old_str:str = PlayerRanks[p]['Rank'].lower()
                PlayerRank_rr_old:int = PlayerRanks[p]['rr']
                
                PlayerRank_new_str = Ranks['data']['current']['tier']['name'].lower()
                PlayerRank_rr_new:int = Ranks['data']['current']['rr']
                PlayerRank_new_int = (list(rank_emoji_dic).index(PlayerRank_new_str)+1)*100+PlayerRank_rr_new

                sp = ' ' #  for space formatting in response

                if not PlayerRank_old_str == "":
                    PlayerRank_old_int = (list(rank_emoji_dic).index(PlayerRank_old_str)+1)*100+PlayerRank_rr_old
                    newRank_base_respose:str = PlayerRank_new_str.title() + sp + rank_emoji_dic[PlayerRank_new_str] + sp + "RR:" + str(PlayerRank_rr_new)
                    oldRank_base_respose:str = PlayerRank_old_str.title() + sp + rank_emoji_dic[PlayerRank_old_str] + sp + "RR:" + str(PlayerRank_rr_old)

                else: 
                    PlayerRank_old_int = 0
                    newRank_base_respose:str = PlayerRank_new_str.title() + sp + rank_emoji_dic[PlayerRank_new_str] + sp + "RR:" + str(PlayerRank_rr_new)
                    oldRank_base_respose = ""
                

                # if no rank previous
                if PlayerRank_old_int == 0:
                    RankMove = 'new'
                    response_step = p.upper() + " : " + newRank_base_respose + "  :  " + "New Rank Added"
                    PlayerRanks[p]['Rank'] = PlayerRank_new_str
                    PlayerRanks[p]['rr'] = PlayerRank_rr_new
                    PlayerRanks[p]['DateOfRank'] = str(datetime.now().strftime(date_timeFormat))
                                        
                #No Rank Change
                elif PlayerRank_old_int == PlayerRank_new_int:
                    #RankMove = 'same'
                    #response_step = playerName.upper() + " : " + newRank_base_respose + "  :  " + "No Change"
                    PlayerRanks[p]['DateOfRank'] =  str(datetime.now().strftime(date_timeFormat))
                    response_step = ""
                
                #if rank has changed
                elif not PlayerRank_old_int == PlayerRank_new_int: 
                
                    PlayerRanks[p]['Rank'] = PlayerRank_new_str
                    PlayerRanks[p]['rr'] = PlayerRank_rr_new
                    PlayerRanks[p]['DateOfRank'] =  str(datetime.now().strftime(date_timeFormat))
                    

                    magnitude = PlayerRank_new_int - PlayerRank_old_int
                    
                    xMag:str = "lowMag"
                    if abs(magnitude) >100: xMag = "highMag"
                    
                    if magnitude > 0:
                        RankMove = 'positive'
                                
                    elif magnitude < 0:
                        RankMove = 'negative'

                    else:
                        pass

                    #repsonse
                    RankMovePhrase:str = random.choice(rank_key_phrase[RankMove][xMag])
                    response_step = p.upper() + " : " + oldRank_base_respose + "  🡆  " + newRank_base_respose + "  :  " + RankMovePhrase.capitalize() 
                
                #Error Catch
                else:
                    logger.error(response_step = f'UPDATE RANKS : ERROR -- {p} rank movement check error')
                    response_step = ""
                
                if not response_step == "":
                    response.append(response_step) 
                    PlayerRanks[p]['callError'] = 0
                    PlayerRanks[p]['RunsWithNoChange'] = 0

                else:
                    PlayerRanks[p]['RunsWithNoChange']+=1

                logger.info(f'UPDATE RANKS : MAG {magnitude} : {p.encode("utf8")} -- old {PlayerRank_old_int} : new {PlayerRank_new_int}') 
                
            #if player not found
            else:
                response.append(f':x: {p} -- Error on Player Data')
                PlayerRanks[p]['callError'] += 1
                logger.error(f'UPDATE RANKS : ERROR -- {p} !! PLAYER NOT FOUND !! - Check json file')

        
        except Exception as err:
            logger.error(f'UPDATE RANKS : ERROR -- {p} !! Exeption : {err} :: {type(err)}!!')
            PlayerRanks[p]['callError'] += 1

        with open(RanksPlayerRanks_json, 'w') as json_file:
            json.dump(PlayerRanks, json_file, indent = 4)

    return response


#commands
class rank(commands.Cog):
    def __init__(self,bot):
        self.bot = bot
    
    #Update all ranks listed in "/data/PlayeRanks.json"
    @app_commands.command(name="update_ranks", description="Update and show the ranks of all players")
    async def UpdateRanks(self, interaction:discord.Interaction):
        await interaction.response.defer()
        with open(RanksPlayerRanks_json,'r') as json_file:
               playerRanks = json.load(json_file)
       
        lastUpdate = Latest_Timestamp(playerRanks)


        if len(playerRanks) == 0:
            await interaction.followup.send("```no players in data```")
            pass
        
        else:
            await ValRank_API_update(playerRanks)
            messageResponse:list = list(UpdateRanks_function(playerRanks))
        
        embed = discord.Embed(title='UPDATE RANKS : ', description="",  color=discord.Color.dark_gray())  
        if not len(messageResponse) == 0:
            for message in messageResponse:
                embed.add_field(name=message, value='', inline=False)
        else:
            embed.add_field(name="no changes to ranks from last update (use /show_ranks to see all ranks)", value='', inline=False)
            
        with open(RanksPlayerRanks_json,'r') as json_file:
            playerRanks = json.load(json_file)
        
        thisUpdate = Latest_Timestamp(playerRanks)
        
        embed.set_footer(text=f'Updated from {lastUpdate} to {thisUpdate}')
        logger.info('UPDATE RANKS : -- COMPLETED --')
        
        await interaction.followup.send(embed=embed)


        
        

    @app_commands.command(name="show_ranks", description="Show the ranks of all players")
    async def showRanks(self, interaction:discord.Interaction):

        with open(RanksPlayerRanks_json,'r') as json_file:
            playerRanks = json.load(json_file)
        
        with open(RanksEmojis_json,'r') as json_file:
            rankEmoji_dic = json.load(json_file)
        
        embed = discord.Embed(title='RANKS : ', description="",  color=discord.Color.dark_gray())  
        
        for p in playerRanks:
            rank = playerRanks[p]['Rank']
            rr = playerRanks[p]['rr']
            emoji = rankEmoji_dic[rank]
            
            with open(f'{RanksAPI_Folder}/{p}.json') as json_file:
                    Ranks = json.load(json_file)
                
            recent =  list(Ranks['data']['seasonal'])[-1]       
            season  = recent['season']['short'].upper()
              
            msg = f"{p.title()} : {season} : {rank.title()} {emoji} RR: {rr}"
        
            embed.add_field(name=msg, value='', inline=False)
        
        embed.set_footer(text=f'Data as at : {Latest_Timestamp(playerRanks)}')
        
        await interaction.response.send_message(embed=embed)


    @app_commands.command(name="latest_season_win_loss",description="Show the win/loss of all players for thier latest season")
    async def showWinLoss(self, interaction:discord.Interaction):
        
        playerRanks = PlayerRanksDict()
        embed = discord.Embed(title='Latest played season win/loss : ', description="",  color=discord.Color.dark_gray())  
       
        for p in playerRanks:   
            with open(f'{RanksAPI_Folder}/{p}.json') as json_file:
                Ranks = json.load(json_file)
            
            recent =  list(Ranks['data']['seasonal'])[-1]       
            wins    = recent['wins']
            games   = recent['games']
            season  = recent['season']['short'].upper()
            
            msg = f"{p} : {season} : wins/games = {wins}/{games} ({round(wins/games*100,0)}%)"
            embed.add_field(name=msg, value='', inline=False)
            logger.info (msg)
        
        embed.set_footer(text=f'Data as at : {Latest_Timestamp(playerRanks)}')
        await interaction.response.send_message(embed=embed)


    @app_commands.command(name='highest_rank', description = 'Season and highest rank for each player')
    async def HighestRank(self, interaction: discord.Interaction):
        
        embed =  discord.Embed(title="Highest Ranks", description='',  color=discord.Color.dark_gray())  
   
        playerRanks = PlayerRanksDict()
        
        for p in playerRanks:
            try:
                with open(f'{RanksAPI_Folder}/{p}.json') as json_file:
                    Ranks = json.load(json_file)
                name = Ranks['data']['account']['name']
                tag  = Ranks['data']['account']['tag']
                name = name + "#" + tag
                season = Ranks['data']['peak']['season']['short'].upper()
                rank = Ranks['data']['peak']['tier']['name']
                
                msg =  name + "  :  " + season + " : " + rank
                embed.add_field(name=msg, value='', inline=False)

            except Exception as e:
                logger.error(f'HighestRank : ERROR : {p} : {e}')
                
        embed.set_footer(text=f'Data as at : {Latest_Timestamp(playerRanks)}')
        await interaction.response.send_message(embed=embed)
        
    '''
    @app_commands.command(name='add_player', description = 'Add a player to keep track of thier rank changes')
    async def AddPlayer_Blank(self,interaction: discord.Interaction, player_name:str, player_tag:str):    
            
        player_tag = player_tag.replace("#", "")
        p = player_name + "#" + player_tag
        ephem = False
        
        Plyr = {
        p.lower():{
                'Rank':'',
                "rr":0,
                'DateOfRank':'',
                "callError":0,
                "RunsWithNoChange":0,
                "PUID":""
            }
        }

        playerRanks = PlayerRanksDict()

        if not p.lower() in playerRanks:
            playerRanks.update(Plyr)
            if not playerRanks:
                playerRanks = {}
            
            with open(PlayerRanks,'w') as json_file:
                json.dump(playerRanks,json_file,indent=4)

            response = f'{p} added'

        else:
            response = f'{p} already exists'
            ephem = True
            
        embed =  discord.Embed(title=response, description='',  color=discord.Color.dark_gray())  
        await interaction.response.send_message(embed = embed, ephemeral=ephem)
        logger.info(response)
    '''

    @app_commands.command(name='add_response_suggestion', description = 'suggest a positive or negative response to when the ranks are updated') 
    @app_commands.describe(suggestion_type='the type of response to suggest')
    @app_commands.choices(suggestion_type=[
        app_commands.Choice(name='positive',value='positive'),
        app_commands.Choice(name='negative',value='negative'),
        ])   
    
    async def add_response_suggestion(self,interaction: discord.Interaction, suggestion_type:app_commands.Choice[str], suggestion:str):
        
        bannedChar = set(r"""`*{[}}|\"'""")
        msg:str = ""

        if any (char in suggestion for char in bannedChar):
            msg = f"can't contain characters : {' '.join(bannedChar)}"
            logger.error(f"ADD RESPONSE :: ERROR :: {msg}")
        
        else:
            with open(RanksPhraseResponse_sug_json) as json_file:
                phrases = json.load(json_file)
        
            phrases[suggestion_type.name].append(suggestion)
            
            with open(RanksPhraseResponse_sug_json,"w") as json_file:
                json.dump(phrases, json_file, indent = 4)
            
            msg = f"added {suggestion_type.name} phrase of : {suggestion}"
            logger.info(f"ADD RESPONSE :: ADDED :: {suggestion_type.name.upper()} :: {suggestion}")
        
        await interaction.response.send_message(msg, ephemeral=True)
            

    @commands.command(name="LRU", description = "Get latest 'DateOfRank' in PLayerRanks.json")
    @commands.is_owner()
    async def LatestRanksUpdate(self, ctx):
        if AdminMessageConditions(ctx):
            with open(RanksPlayerRanks_json,'r') as json_file:
                playerRanks = json.load(json_file)
                
            response:str = f'```Latest timestamp = {Latest_Timestamp(playerRanks)}```'

            logger.info(response)
            await ctx.send("```" + response + "```")


    @commands.command(name="call_CallErrors", description = "Show players that have API call errors in the data")
    @commands.is_owner()
    async def call_CallErrors(self, ctx):
        if AdminMessageConditions(ctx):
            response:str = ""
 
            playerRanks = PlayerRanksDict()

            for p in playerRanks:
                callErr = playerRanks[p]['callError']
                if not callErr == 0:
                    response = f'{p} has {callErr} call errors'
                
            if response == '': response = "There are no players with call erorrs"
            
            logger.info(response)
            await ctx.send("```" + response + "```" )


    @commands.command()
    @commands.is_owner()
    async def clear_CallErrors(self, ctx):
        if AdminMessageConditions(ctx):
        
            playerRanks = PlayerRanksDict()

            for  p in playerRanks:
                playerRanks[p]['callError'] = 0

            with open(RanksPlayerRanks_json,'w') as json_file:
                json.dump(playerRanks, json_file, indent = 4)

            response = "Cleared all call Errors in PlayersRanks"
            logger.info(response)
            await ctx.send("```" + response + "```")


    @commands.command(name="pop_CallErrors", description="remove all players in player ranks that have call errors greater than input")
    @commands.is_owner()
    async def pop_CallErrors(self, ctx, greaterThan:int = 0):
        if AdminMessageConditions(ctx):
         
            playerRanks = PlayerRanksDict()
            removedPlayers:list = []

            for p in playerRanks:
                if playerRanks[p]['callError'] > int(greaterThan):
                    removedPlayers.append(p)

            if len(removedPlayers) > 0:
                for k in removedPlayers:
                    playerRanks.pop(k)

                with open(RanksPlayerRanks_json,'w') as json_file:
                    json.dump(playerRanks, json_file, indent = 4)

                response = (', ').join(removedPlayers)
                
            else:
                response = "NONE"


            response = f"Removed from Players :  {response}"
            
            logger.info(f"POP CALL ERRORS : > {greaterThan} : {response}")
            await ctx.send("```" + response + "```")
        else:
            
            logger.error(f"POP CALL ERRORS : called in a server")
          
async def setup(bot):
    await bot.add_cog(rank(bot))
