import datetime
import json 

import discord
from discord.ext import commands
from discord import app_commands

from logs.log_settings import logger
from Val_Matches_API import Single_ValMatch_API_update


def PlayerMatchData(player:str, matchType:str = "Competitive"):
    GMT_Adj = datetime.timedelta(hours=11)
    Single_ValMatch_API_update(player)

    with open(f'data\MatchHistoryAPI\{player}.json','r') as json_file:
        playerMatches = json.load(json_file)
    
    ret:dict = {}
    MatchesShown = 5
    Last_5_MatchIDs = list(playerMatches)[0:MatchesShown]
    Last_5_MatchIDs = []

    if not matchType == 'All':
        for match in playerMatches:
            if playerMatches[match]['match']['queue']['name'] == matchType:
                Last_5_MatchIDs.append(match)
    
    #to catch if less than 5 comp games etc
    numMatches = len(Last_5_MatchIDs)
    if numMatches < MatchesShown:
        Last_5_MatchIDs = Last_5_MatchIDs[0:numMatches]
        MatchesShown = numMatches
    else:
        Last_5_MatchIDs = Last_5_MatchIDs[0:MatchesShown]

    resp_pg1 = ''
    resp_pg2 = ''
    resp_pg3 = ''
    resp_pg4 = ''

    for i in range(0,len(Last_5_MatchIDs)):
        m = playerMatches[Last_5_MatchIDs[i]]
        mData = m['match']
        tData = m['teams']

        mStart  = mData['started_at'].split('T')
        mStartDay  = mStart[0]
        mStartTime = mStart[1].split('.')[0][:5]
        mStart = datetime.datetime.strptime(mStartDay + " " + mStartTime,"%Y-%m-%d %H:%M")
        mStart+=GMT_Adj
        
        mMap = mData['map']['name']
    
        pData  = m['player'][player]
        
        pTeam = pData['team_id']
        # for teams 0 = red and 1 = blue
        PlayerTeam = ['Red', 'Blue']
        playerTeamIndx = PlayerTeam.index(pTeam)
        if tData[playerTeamIndx]['won'] == True:
            pWon = 'WON'
        else:
            pWon = 'LOST'

        pRoundsWon = tData[playerTeamIndx]['rounds']['won']    
        pRoundsLost = tData[playerTeamIndx]['rounds']['lost']
        pRoundWL = f'Rounds Won {pRoundsWon} / {pRoundsLost}'
        
        pAgent = pData['agent']['name']
        pStats = pData['stats']
        pShotsTaken = (pStats['headshots']+pStats['bodyshots']+pStats['legshots'])
        pHeadShot_Perc = round((pStats['headshots']/pShotsTaken)*100,None)

        pK = pStats['kills']
        pD = pStats['deaths']
        pA = pStats['assists']
        pScore = "{:,}".format(pStats['score'])
        pKDA = f'{pK}/{pD}/{pA}'
        pDmg = "{:,}".format(pStats['damage']['dealt'])
        
        #figure out a better way to label - potench dict of all agent abilities to source names
        pAbilityAll = ', '.join([f"{k.capitalize()} : {v}" for k,v in pData['ability_casts'].items()])
        #fix format -- ok for now    
        pBehavior =', '.join([f"{k.capitalize()} : {v}" for k,v in pData['behavior'].items()])

        #Turn this into embed pages on discord
        resp_pg1+= '\n' + f'{i+1} : {mStart.strftime("%d-%m-%y %H:%M")} : {mMap.ljust(10)}  : {pRoundWL.ljust(20)} :  {pWon.ljust(5)} : {pAgent.ljust(10)} : K/D/A {pKDA}'
        resp_pg2+= '\n' + f'{i+1} : Score {pScore} : Damage Dealt {pDmg} : Head Shots {pHeadShot_Perc}%'
        resp_pg3+= '\n' + f'{i+1} : {pAbilityAll}'
        resp_pg4+= '\n' + f'{i+1} : {pBehavior}'

    ret.update({
                'Matches':resp_pg1,
                'Stats':resp_pg2,
                'Ability Cast':resp_pg3,
                'Behaviour':resp_pg4
                })
    return ret

class PaginationView(discord.ui.View):
    current_page:int = 1

    async def send(self, interaction):        
        self.message = await interaction.edit(view=self)
        await self.update_message()

    async def update_message(self):
        self.TotalPages:int = len(self.data)
        currentKey = list(self.data)[self.current_page-1]
        DataShown = self.data[currentKey]

        self.update_buttons()

        embed = discord.Embed(title=f"Player Competitive Match Data :")
        embed.set_footer(text=f"pg. {self.current_page} / {self.TotalPages}")
        embed.add_field(name=currentKey, value=DataShown, inline=False)
        
        await self.message.edit(embed=embed, view=self)

    def update_buttons(self):
        if self.current_page == 1:
            self.prev_button.disabled = True
            self.prev_button.style = discord.ButtonStyle.gray
        else:
            self.prev_button.disabled = False
            self.prev_button.style = discord.ButtonStyle.primary

        if self.current_page == self.TotalPages:
            self.next_button.disabled = True
            self.next_button.style = discord.ButtonStyle.gray
        else:
            self.next_button.disabled = False
            self.next_button.style = discord.ButtonStyle.primary


    @discord.ui.button(label="<",style=discord.ButtonStyle.primary)
    async def prev_button(self, interaction:discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        self.current_page -= 1
        await self.update_message()

    @discord.ui.button(label=">",style=discord.ButtonStyle.secondary)
    async def next_button(self, interaction:discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        self.current_page += 1
        await self.update_message()


class match(commands.Cog):
    def __init__(self,bot):
        self.bot = bot

    @app_commands.command(name="match_update", description="Get player's match history")
    @app_commands.choices(player=[
        app_commands.Choice(name="ewokland#007", value="ewokland#007"),
        app_commands.Choice(name="thesouthtowerr#nyc", value="thesouthtowerr#nyc"),
        app_commands.Choice(name="iq lovï#9999", value="iq lovï#9999"),
        app_commands.Choice(name="asi4n cr34m p13#acpie", value="asi4n cr34m p13#acpie"),
        app_commands.Choice(name="twxlxght#985", value="twxlxght#985"),
        app_commands.Choice(name="boot6#oce", value="boot6#oce"),
        ])

    async def match_update(self, interaction:discord.Interaction, player:str):
        logger.info(f"UPDATE MATCH : {player} : -- RUN --")
        await interaction.response.defer()
        msg = await interaction.original_response()
        
        pagination_view = PaginationView(timeout=None)
        pagination_view.data = PlayerMatchData(player)
        await pagination_view.send(msg)
        logger.info(f"UPDATE MATCH : {player} : -- END --")

async def setup(bot):
    await bot.add_cog(match(bot))

