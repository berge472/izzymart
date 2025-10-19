from datetime import datetime, timedelta, timezone
from typing import Annotated, Optional
from bson import ObjectId
import os


from fastapi import Depends, FastAPI, HTTPException, status, Security
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel
from api.serializeObjects import serializeDict
from config.db import db
from api.users.userModels import UserModel

from util.configUtil import getConfiguration

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

default_root_passwd = os.getenv('ROOT_PASSWD', 'root')


role_hierarchy = {
    "root":100,
    "admin" : 5,
    "maintainer" : 4,
    "user" : 3,
    "guest" : 2,
    "read-only" : 1,
    "pending" : 0
}

class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str | None = None


def checkAndCreateAdmin():
    if db.users.count_documents({}) == 0:
        # Bcrypt has a 72-byte limit, truncate the password bytes if necessary
        passwd_bytes = default_root_passwd.encode('utf-8')
        if len(passwd_bytes) > 72:
            passwd_bytes = passwd_bytes[:72]
        passwd_to_hash = passwd_bytes.decode('utf-8', errors='ignore')

        newUser = {
            "_id": ObjectId('000000000000000000000000'),
            "username": "root",
            "email": "",
            "role": "root",
            "password": pwd_context.hash(passwd_to_hash),
        }

        db.users.insert_one(newUser)


def get_user( username: str):
    user = db.users.find_one({"username": username})
    
    if user is not None:
        user_dict = serializeDict(user)
        return UserModel(**user_dict)

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def authenticate_user(username: str, password: str):
    user = get_user( username)
    if not user:
        return False
    if not verify_password(password, user.password):
        return False
    return user

def create_access_token(data: dict, expires_delta: timedelta | None = None, expires : datetime | None = None):
    to_encode = data.copy()
    currentConfig = getConfiguration()

    expire = None

    if expires:
        expire = expires
    elif expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, currentConfig['secret_key'], algorithm= currentConfig['algorithm'])
    return encoded_jwt

def get_token_user(token: Annotated[str, Depends(oauth2_scheme)]):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    

    currentConfig = getConfiguration()

    try:
        payload = jwt.decode(token, currentConfig['secret_key'], algorithms=[currentConfig['algorithm'] ])

        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user = get_user( username=token_data.username)
    if user is None:
        raise credentials_exception
    return user





def get_current_user( role: Optional[str] = None):

    def role_checker(token: Annotated[str, Depends(oauth2_scheme)]):
    

        user = None
        requiredLevel = 0

        if role is not None:
            requiredLevel = role_hierarchy[role]

        #If there are no users, then behave as admin
        if db.users.count_documents({}) == 1:
            resp = db.users.find_one()
            user = UserModel(**resp)
        else:
            user = get_token_user(token)

        level = role_hierarchy[user.role]

        if level < requiredLevel:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Operation requires {role} role",
            )
        
        return user
    return role_checker




