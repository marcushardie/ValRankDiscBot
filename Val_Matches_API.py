
import os 
import json

import asyncio
import aiohttp
import requests

from dotenv import load_dotenv
from logs.log_settings import logger

#API -------------------
# Riots match history only goes back 1 month and 100 matches

load_dotenv()
API_KEY:str = os.getenv('HENRICK_DEV_APIKEY')
API_Headers = {'accept' : 'application/json', 'Authorization' : API_KEY}


def Single_ValMatch_API_update(p_in):
    p_split = p_in.split("#")
    pass_playerName =  p_split[0]
    pass_playerTag  =  p_split[1]
    response  = requests.get(f'https://api.henrikdev.xyz/valorant/v4/matches/ap/pc/{pass_playerName}/{pass_playerTag}', headers=API_Headers)
   
    loggerHeader:str = "API UPDATE MATCH"
    logger.info(f"{loggerHeader} : START")
    response_status = response.status_code
    try:
        logger.info(f'API UPDATE MATCH : Status {response_status} : {p_in}')
        if response_status==200:
            logger.info(f'API UPDATE MATCH : Status {response_status} : {p_in}')
            datas = response.json()
            matchData = {}
         
            logger.info(f"{loggerHeader} : {p_in}")
            for data in datas['data']:
                    matchId = data['metadata']['match_id']
                    
                    matchData.update({matchId:{}})
                    match = matchData[matchId]
                    match.update({'match':data['metadata']})
                    match.update({'teams':data['teams']})

                    for pData in data['players']:
                        playerName:str = pData['name']
                        playerTag:str  = pData['tag']
                        plyr = playerName + "#" + playerTag

                        if p_in == plyr.lower():
                            match.update({'player':{p_in:{}}})
                            plyr = match['player'][p_in]
                            plyr.update(pData)
                            
                            fileName:str = f'data/MatchHistoryAPI/{p_in}.json'

                            try:  
                                with open(fileName) as json_file:
                                    existingData = json.load(json_file)
                                if not existingData == matchData:
                                    dictMerge = matchData.copy()
                                    dictMerge.update(existingData)
                                    logger.info(f'{loggerHeader} : {p_in} Merged and updated')
                                    
                                else:
                                    logger.info(f'{loggerHeader} : {p_in} no Update')
                                    pass                                    
                            except:
                                dictMerge = matchData
                                logger.info(f'{loggerHeader} : {p_in} New and updated')
                               
                                
                            with open(fileName,'w+') as json_file:
                                json.dump(dictMerge,json_file,indent=4)
        else:   
            logger.error(f'API Response Error : {response_status}')
            

    except Exception as e:
        logger.error(f"{loggerHeader} : ERROR -- Exeption -- {p_in} : {e}")
        
    logger.info(f"{loggerHeader} : END")
