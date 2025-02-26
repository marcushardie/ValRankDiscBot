import os 
import logging
from datetime import datetime
from logging.config import dictConfig
from dotenv import load_dotenv

load_dotenv()

#For run history
now = str(datetime.now().strftime("%H-%M-%S"))
day = str(datetime.now().strftime("%y-%m-%d"))

fileHead = 'logs'
fileLoc = fileHead + '/history/' + day +'/'+ now
FileName_Infos = fileLoc+'/--INFO' + '.log'
FileName_Warns = fileLoc+'/--WARN' + '.log'

if not os.path.isdir(fileLoc):
    os.makedirs(fileLoc)

LOGGING_CONFIG = {
    "version":1,
    "disabled_existing_loggers" : True,
    "formatters":{
        "verbose":{
            "format": "%(levelname)-10s - %(asctime)s - %(module)-15s : %(message)s"
        },
        "standard":{
            "format": "%(levelname)-10s - %(name)-15s : %(message)s"
        }
    },
    "handlers":{
        "console_1":{
            "level" : "DEBUG",
            "class": "logging.StreamHandler",
            "formatter":"standard"
        },
        "console_2":{
            "level" : "WARNING",
            "class": "logging.StreamHandler",
            "formatter":"standard"
        },
        "file_History_INFO":{
            "level" : "INFO",
            "class": "logging.FileHandler",
            "filename": FileName_Infos,
            "mode":"w",
            "formatter":"verbose"
        },
        "file_History_WARN":{
            "level" : "WARNING",
            "class": "logging.FileHandler",
            "filename": FileName_Warns, 
            "mode":"w",
            "formatter":"verbose"
        },
        "file_ThisRun":{
            "level" : "INFO",
            "class": "logging.FileHandler",
            "filename": fileHead+"/infos.log",
            "mode":"w",
            "formatter":"verbose"
        }
    },
    "loggers":{
        "bot":{
            "handlers":["console_1","file_ThisRun","file_History_INFO"],
            "Level": "INFO",
            "propagate":False
        },
        "discord":{
            "handlers":["console_2","file_ThisRun","file_History_WARN"],
            "Level": "INFO",
            "propagate":False
        }
    }
}

dictConfig(LOGGING_CONFIG)
logger = logging.getLogger("bot")
