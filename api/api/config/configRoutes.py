from bson import ObjectId
from fastapi import status 
from fastapi import APIRouter
from config.db import db
from api.serializeObjects import serializeDict, serializeList

from fastapi import status , Depends
from api.users.userModels import UserModel
from util.authUtil import get_current_user
from typing import Annotated

import secrets

from api.config.configModel import ConfigModel
from util.configUtil import getConfiguration


configRoutes = APIRouter()



@configRoutes.get("")
async def getConfig(useCache: bool = False):   
    
    obj = getConfiguration(useCache)


    obj.pop("secret_key")
    obj.pop("algorithm")

    return obj

@configRoutes.put("")
async def updateConfig(config: ConfigModel, current_user: Annotated[UserModel, Depends(get_current_user('admin'))] ):

    config_dict = config.model_dump(exclude_none=True)
    config_dict.pop('id', None)
    config_dict.pop('secret_key', None)
    config_dict.pop('algorithm', None)

    resp = db.config.update_one({}, {"$set": config_dict})


    obj = getConfiguration(False)
    obj.pop("secret_key")
    obj.pop("algorithm")

    #return updated config


    return obj


