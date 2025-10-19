from bson import ObjectId
from fastapi import status , Depends, HTTPException, Body
from fastapi.responses import FileResponse
from typing import Annotated
from util.authUtil import get_current_user
from fastapi import APIRouter
from config.db import db
from api.users.userModels import UserModel
from api.serializeObjects import serializeDict, serializeList
from passlib.context import CryptContext
from api.config.configRoutes import getConfiguration
from api.files.fsFileRoutes import add_fsFile_reference, remove_fsFile_reference
from importlib.resources import files
from tempfile import mkdtemp
from util.jobQueue import JobQueue
import os


from fastapi import Depends
import yaml


jobRoutes = APIRouter()
_jobs = JobQueue()

@jobRoutes.get("")
async def getAll( current_user: Annotated[UserModel, Depends(get_current_user('user'))] ):
        
        jobs = _jobs.getJobs()

        return [job.toDict() for job in jobs]
        

@jobRoutes.get( "/{id}")
async def getOne(id: str, current_user: Annotated[UserModel, Depends(get_current_user('user'))]):

    try:
          return _jobs.getJob(id).toDict()
    except Exception as e:
        raise HTTPException(status_code=404, detail="Job not found")
    
@jobRoutes.get("/{id}/files/{label}")
async def downloadJobFile(id: str, label: str, current_user: Annotated[UserModel, Depends(get_current_user('user'))] ):
    try:
        job = _jobs.getJob(id)
        file = job.getFile(label)
        if not file:
            raise HTTPException(status_code=404, detail="File not found")
        
        if os.path.exists(file.path):
            return FileResponse(file.path, media_type="application/octet-stream", filename=os.path.basename(file.path))

        
        return file
    except Exception as e:
        raise HTTPException(status_code=404, detail="Job not found")
    
    
@jobRoutes.put("/{id}/response")
async def respondToJob(id: str, response: str, current_user: Annotated[UserModel, Depends(get_current_user('user'))] ):
    try:
        job = _jobs.getJob(id)
        ack = job.respond(response)

        return ack
    except Exception as e:
        raise HTTPException(status_code=404, detail="Job not found")
    
@jobRoutes.delete("/{id}")
async def deleteJob(id: str, current_user: Annotated[UserModel, Depends(get_current_user('user'))] ):
    try:
        return _jobs.removeJob(id)
    except Exception as e:
        raise HTTPException(status_code=404, detail="Job not found")