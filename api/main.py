from fastapi import FastAPI, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from typing import Annotated
from api.users.userModels import UserModel
from util.authUtil import get_current_user

from api.config.configRoutes import getConfiguration
from config.db import db
from bson import ObjectId

import asyncio

from api.users.userRoutes import userRoutes
from api.config.configRoutes import configRoutes
from api.auth.authRoutes import authRoutes
from api.backup.backupRoutes import backupRoutes
from api.files.fsFileRoutes import fileRoutes
from api.jobs.jobRoutes import jobRoutes
from api.product.productRoutes import productRoutes
import time
from typing import Callable

from util.authUtil import checkAndCreateAdmin



import logging

app = FastAPI()
base = "/api/v1"
oauth2_scheme = OAuth2PasswordBearer(tokenUrl= "api/v1/auth/token")
currentConfig = None


@app.on_event("startup")
async def startup_event():
    pass

# Allow requests from all origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

@app.middleware("http")
async def add_process_time_header(request: Request, call_next: Callable):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response


app.include_router(userRoutes, tags=["users"], prefix= base +  "/users")
app.include_router(configRoutes, tags=["configuration"], prefix= base +   "/configuration")
app.include_router(authRoutes, tags=["authentication"], prefix= base +  "/auth")
app.include_router(backupRoutes, tags=["backup"], prefix= base +  "/backups"  )
app.include_router(fileRoutes, tags=["files"], prefix= base +  "/files"  )
app.include_router(jobRoutes, tags=["jobs"], prefix= base +  "/jobs"  )
app.include_router(productRoutes, tags=["products"], prefix= base +  "/products"  )

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get(base+ "/test")
async def test(current_user: Annotated[UserModel, Depends(get_current_user('user'))] ):
    return {"message": "API GOOD"}

@app.get("/secure-endpoint")
def secure_endpoint(token: str = Depends(oauth2_scheme)):
    # Your endpoint logic here
    return {"message": "Secure data"}

logging.getLogger("uvicorn.access").setLevel(logging.CRITICAL)


getConfiguration()
checkAndCreateAdmin()
