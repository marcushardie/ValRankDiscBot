
import os 
import json

import asyncio
import aiohttp
import requests

from dotenv import load_dotenv
from logs.log_settings import logger

#API -------------------
load_dotenv()
API_KEY:str = os.getenv('HENRICK_DEV_APIKEY')
API_Headers = {'accept' : 'application/json', 'Authorization' : API_KEY}

def get_tasks_UpdateRanks(session,PlayerRanks):
    tasks = []

    for p in PlayerRanks:
        p = p.split("#")
        pass_playerName =  p[0]
        pass_playerTag  =  p[1]
     
        api_url = f'https://api.henrikdev.xyz/valorant/v3/mmr/ap/pc/{pass_playerName}/{pass_playerTag}'
        tasks.append(asyncio.create_task(session.get(api_url, headers=API_Headers, ssl=False)))
    
    return tasks


async def ValRank_API_update(PlayerRanks):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    async with aiohttp.ClientSession() as session:
        tasks = get_tasks_UpdateRanks(session,PlayerRanks)
        responses  = await asyncio.gather(*tasks)
        
        loggerHeader:str = "API UPDATE RANK"
        logger.info(f"{loggerHeader} : START")

        for response in  responses:
            data = await response.json()
            try:
                if data['status'] == 200:
                    playerName = f"{data['data']['account']['name']}#{data['data']['account']['tag']}"
                    
                    with open(f'data/Rank_valorantApi/{playerName}.json','w+') as json_file:
                        json.dump(data, json_file, indent = 4)
                    
                    logger.info(f"{loggerHeader} : {playerName}")
                    
                else:
                    logger.error(f"{loggerHeader} : ERROR -- {playerName} : API ErrorCode: {data['status']}")
        
            except Exception as e:
                logger.error(f"{loggerHeader} : ERROR -- Exeption -- {playerName} : {e}")
        
    logger.info(f"{loggerHeader} : END")
