from bson import ObjectId
from fastapi import status , Depends
from typing import Annotated
from util.authUtil import get_current_user
from fastapi import APIRouter
from config.db import db
from api.users.userModels import UserModel
from api.serializeObjects import serializeDict, serializeList
from passlib.context import CryptContext
from api.config.configModel import registrationScheme
from api.config.configRoutes import getConfiguration 
from util.configUtil import getConfiguration
from fastapi import HTTPException

from fastapi import Depends

from api.users.userSchemas import userEntity, usersEntity

userRoutes = APIRouter()


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")




@userRoutes.get("")
async def getAll( current_user: Annotated[UserModel, Depends(get_current_user('admin'))] ):

    return usersEntity(db.users.find())

@userRoutes.get( "/{id}")
async def getOne(id: str, current_user: Annotated[UserModel, Depends(get_current_user('user'))]):
    return userEntity(db.users.find_one({"_id": ObjectId(id)}))

@userRoutes.put("/{id}")
async def updateOne(id: str, user: UserModel, current_user: Annotated[UserModel, Depends(get_current_user('admin'))] ):

    if current_user.role not in ['admin', 'root'] and current_user.id != id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User does not have permission to update this user",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_dict = user.model_dump(exclude_none=True)

    if current_user.role != 'admin' and current_user.role != 'root':
        user_dict.pop('role', None)
    
    user_dict.pop('id', None)
    user_dict.pop('password', None)

    resp = db.users.update_one({"_id": ObjectId(id)}, {"$set": user_dict})
    return {"message": "User updated"}

@userRoutes.put( "/{id}/role")
async def updateRole(id: str, role: str, current_user: Annotated[UserModel, Depends(get_current_user('admin'))] ):

    if role not in ['admin', 'maintainer', 'user', 'guest', 'pending']:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid role",
            headers={"WWW-Authenticate": "Bearer"},
        )

    
    resp = db.users.update_one({"_id": ObjectId(id)}, {"$set": {"role": role}})
    return {"message": "Role updated"}

@userRoutes.post("")
async def createOne(user: UserModel, current_user: Annotated[UserModel, Depends(get_current_user('admin'))] ):

    user_dict = user.model_dump(exclude_none=True)
    user_dict.pop('id', None)
    user_dict.pop('password', None)

    resp = db.users.insert_one(user_dict)
    return {"message": "User created"}

@userRoutes.delete("/{id}")
async def deleteOne(id: str, current_user: Annotated[UserModel, Depends(get_current_user('admin'))] ):

    
    #Check for root 
    user = db.users.find_one({"_id": ObjectId(id)})

    if user == None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    

    if user['role'] == 'root':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot delete root user",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    db.users.delete_one({"_id": ObjectId(id)})
    return {"message": "User deleted"}



