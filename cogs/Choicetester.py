# import asyncio
# import json
# import random
# import typing
# import enum
# from datetime import datetime

import discord
from discord.ext import commands
from discord import app_commands

# from logs.log_settings import logger
# from cogs.Admin import AdminMessageConditions,AdminMessageConditions_Slash
# from Val_Matches_API import ValMatch_API_update
# from cogs.Rank import RanksPlayerRanks_json

    

class choicetester(commands.Cog):
    def __init__(self,bot):
        self.bot = bot

    # async def fruit_autocomplete(
    #     interaction: discord.Interaction,
    #     current: str,
    # ) -> list[app_commands.Choice[str]]:
    #     fruits = ['Banana', 'Pineapple', 'Apple', 'Watermelon', 'Melon', 'Cherry']
    #     return [
    #         app_commands.Choice(name=fruit, value=fruit)
    #         for fruit in fruits if current.lower() in fruit.lower()
    #     ]

    # @app_commands.command()
    # @app_commands.autocomplete(fruit=fruit_autocomplete)
    # async def fruits(interaction: discord.Interaction, fruit: str):
    #     await interaction.response.send_message(f'Your favourite fruit seems to be {fruit}')
    pass
async def setup(bot):
    await bot.add_cog(choicetester(bot))
