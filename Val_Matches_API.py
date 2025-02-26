
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

# def get_tasks_UpdateMatches(session,PlayerRanks):
#     tasks = []
#     for p in PlayerRanks:
#         p = p.split("#")
#         pass_playerName =  p[0]
#         pass_playerTag  =  p[1]
#         api_url = f'https://api.henrikdev.xyz/valorant/v4/matches/ap/pc/{pass_playerName}/{pass_playerTag}'
#         logger.info(f'API UPDATE MATCH : Pulling API : {p}')
#         tasks.append(asyncio.create_task(session.get(api_url, headers=API_Headers, ssl=False)))

#     return tasks

# #updateMatch
# async def ValMatch_API_update(PlayerRanks):
#     async with aiohttp.ClientSession() as session:
#         tasks = get_tasks_UpdateMatches(session,PlayerRanks)
#         responses  = await asyncio.gather(*tasks)
        
#         loggerHeader:str = "API UPDATE MATCH"
#         logger.info(f"{loggerHeader} : START")
        
#         for response in  responses:
#             try:
#                 if response.status==200:
#                     datas = await response.json()
#                     matchData = {}
#                     pR = "#".join(response._request_info.url.parts[6:])
#                     logger.info(f"{loggerHeader} : {pR}")

#                     for data in datas['data']:
#                             matchId = data['metadata']['match_id']
                            
#                             matchData.update({matchId:{}})
#                             match = matchData[matchId]
#                             match.update({'match':data['metadata']})
#                             match.update({'teams':data['teams']})

#                             for p in data['players']:
#                                 playerName:str = p['name']
#                                 playerTag:str  = p['tag']
#                                 plyr = playerName + "#" + playerTag

#                                 if pR == plyr.lower():
#                                     match.update({'player':{plyr:{}}})
#                                     plyr = match['player'][plyr]
#                                     plyr.update(p)
                                    
#                                     fileName:str = f'data/MatchHistoryAPI/{pR}.json'

#                                     try:  
#                                         with open(fileName) as json_file:
#                                             existingData = json.load(json_file)
#                                         if not existingData == matchData:
#                                             dictMerge = matchData.copy()
#                                             dictMerge.update(existingData)
#                                             logger.info(f'{loggerHeader} :{pR} Merged and updated')
#                                         else:
#                                             logger.info(f'{loggerHeader} :{pR} no Update')
                                            
#                                     except:
#                                         dictMerge = matchData
#                                         logger.info(f'{loggerHeader} :{pR} New and updated')
                                        
#                                     with open(fileName,'w+') as json_file:
#                                         json.dump(dictMerge,json_file,indent=4)

#             except Exception as e:
#                 logger.error(f"{loggerHeader} : ERROR -- Exeption -- {pR} : {e}")
        
#     logger.info(f"{loggerHeader} : END")

# def Full_ValMatch_API_update(p):
#         p = p.split("#")
#         pass_playerName =  p[0]
#         pass_playerTag  =  p[1]
#         response  = requests.get(f'https://api.henrikdev.xyz/valorant/v4/matches/ap/pc/{pass_playerName}/{pass_playerTag}', headers=API_Headers)
#         with open("matchHistory.json",'w+') as json_file:
#             json.dump(response.json() ,json_file,indent=4)


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
                            plyr = match['player'][plyr]
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
