from bson import ObjectId
from datetime import datetime, timedelta, timezone
from fastapi import status 
from fastapi import APIRouter
from config.db import db
from api.users.userModels import UserModel
from api.serializeObjects import serializeDict, serializeList
from passlib.context import CryptContext
from api.config.configRoutes import getConfiguration
from passlib.context import CryptContext
from jose import JWTError, jwt
from fastapi import Depends, FastAPI, HTTPException, status
from typing import Annotated


from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from util.authUtil import authenticate_user, get_user, get_current_user, Token, create_access_token

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
ACCESS_TOKEN_EXPIRE_MINUTES = 1800

authRoutes = APIRouter( )

@authRoutes.post( "/token")
async def getToken(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]) -> Token :


    user = authenticate_user( form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    

    if user.role == 'pending':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is pending approval",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )

    token = Token(access_token=access_token, token_type="bearer")

    return token


@authRoutes.post("/signup")
async def signup(user: UserModel):

    if user.username == '' or user.password == '':
        return {"error": "Username and password are required"}, status.HTTP_400_BAD_REQUEST

    if db.users.find_one({"username": user.username}):
        return {"error": "Username already exists"}, status.HTTP_400_BAD_REQUEST
    
    config = getConfiguration()

    if db.users.count_documents({}) == 1:  #If the only user is root, then this is the first real user, make them an admin
        user.role = 'admin'
    else:

        if config['registration'] == 'none':
            return {"error": "Registration is closed"}, status.HTTP_400_BAD_REQUEST
        elif config['registration']  == 'requireApproval':
            user.role = 'pending'
        else:
            user.role = 'user'


    user.password = pwd_context.hash(user.password)

    newUser = db.users.insert_one(dict(user))
    return serializeDict(db.users.find_one({"_id": newUser.inserted_id}))

@authRoutes.post("/createUser")
async def createUser(user: UserModel, current_user: Annotated[UserModel, Depends(get_current_user('admin'))] ):


    if user.role == None:
        user.role = 'user'

    user.password = pwd_context.hash(user.password)


    newUser = db.users.insert_one(user.model_dump(exclude_none=True))
    return {"message": "User created"}


@authRoutes.post("/ApiKey")
async def createApiKey(newKey: UserModel, expires: datetime, current_user: Annotated[UserModel, Depends(get_current_user('admin'))] ):

    newKey.type = 'apikey'
    newKey.email = ''
    newKey.expires = expires

    inserted = db.users.insert_one(newKey.model_dump(exclude_none=True))

    access_token = create_access_token(
        data={"sub": newKey.username }, expires=expires
    )

    return {"message": "API Key created", "token": access_token}
    


@authRoutes.get("/currentUser")
async def getCurrent( current_user: Annotated[UserModel, Depends(get_current_user('pending'))] ):
    ret = current_user.model_dump(exclude=["password"], exclude_none=True) 
    return ret

@authRoutes.get("/user")
async def getCurrent( current_user: Annotated[UserModel, Depends(get_current_user('user'))] ):
    ret = current_user.model_dump(exclude=["password"], exclude_none=True) 

    return ret

@authRoutes.post("/users/{id}/psswd")
async def changePassword(id: str, password: str, current_user: Annotated[UserModel, Depends(get_current_user('user'))] ):



    if current_user.id == id or current_user.role == 'root':

        hash = pwd_context.hash(password)
        db.users.update_one({"_id": ObjectId(id)}, {"$set": {"password": hash}})

        return {"message": "Password updated"}
    
    else:
        #raise exception 
         raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Permission Denied",
            headers={"WWW-Authenticate": "Bearer"},
        )
        

    
