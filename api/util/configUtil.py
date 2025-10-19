
from fastapi import APIRouter
from config.db import db
from api.serializeObjects import serializeDict, serializeList



import secrets

from api.config.configModel import ConfigModel


currentConfig = None

def getConfiguration(useCache=False):
    global currentConfig

    useCache = False
    
    if currentConfig is None or not useCache:
        currentConfig =  db.config.find_one()

    if currentConfig is None:
        print("No configuration found, creating default configuration")

        #generate secret key

        obj = {
            "registries": [],
            "secret_key": secrets.token_hex(32),
            "algorithm": "HS256"
        }


        newConfig = ConfigModel(**obj)

        inserted = db.config.insert_one(newConfig.model_dump())    
        currentConfig = db.config.find_one({"_id": inserted.inserted_id})

    configModel = ConfigModel(**currentConfig)

    return configModel.model_dump()