from bson import ObjectId
from fastapi import status , Depends
from typing import Annotated
from util.authUtil import get_current_user
from fastapi import APIRouter
from config.db import db, fs
from api.users.userModels import UserModel
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import FileResponse, StreamingResponse
from pymongo import MongoClient
import hashlib

from tempfile import NamedTemporaryFile
from typing import Dict
from api.files.fsFileModel import fsFileModel
import io
import mimetypes
import logging

from fastapi import Depends

logger = logging.getLogger(__name__)


fileRoutes = APIRouter()

def calculate_md5(file):
    """Calculates the MD5 hash of the uploaded file."""
    md5_hash = hashlib.md5()
    for chunk in iter(lambda: file.read(4096), b""):
        md5_hash.update(chunk)
    file.seek(0)  # Reset the file pointer after reading
    return md5_hash.hexdigest()


def remove_fsFile_reference(fsFileId: str, refId: str):
    """Removes a reference from the fsFileModel."""
    file = db.files.find_one({"_id": fsFileId})
    if file is not None:
        references = file.get("references", [])
        if refId in references:
            references.remove(refId)

            #If there are no more references to a file, delete the file from the gridFS collection and the metadata
            if len(references) == 0:
                fileId = file.get("fileId")
                fs.delete(ObjectId(fileId))
                db.files.delete_one({"_id": fsFileId})

            else: #If there are still references, update the references
                db.files.update_one({"_id": fsFileId}, {"$set": {"references": references}})


def add_fsFile_reference(fsFileId: str, refId: str):
    """Adds a reference to the fsFileModel."""
    file = db.files.find_one({"_id": fsFileId})
    if file is not None:
        references = file.get("references", [])
        if refId not in references:
            references.append(refId)
            db.files.update_one({"_id": fsFileId}, {"$set": {"references": references}})


@fileRoutes.get("")
async def getAll( current_user: Annotated[UserModel, Depends(get_current_user('user'))] ):
        

        ret = []

        for x in db.files.find():
            obj = fsFileModel(**x).model_dump(exclude_none=True)
            ret.append(obj)
    
        return ret




@fileRoutes.get( "/{id}")
async def getOne(id: str, current_user: Annotated[UserModel, Depends(get_current_user('user'))]):


    model = db.files.find_one({"_id": ObjectId(id)})


    return fsFileModel(**model).model_dump(exclude_none=True)

@fileRoutes.get("/{id}/image")
async def get_image(id: str):
    """
    Retrieve an image from GridFS by ID.
    Returns the image directly with appropriate content type.
    This endpoint does not require authentication for easy image embedding.
    """
    try:
        file_meta = db.files.find_one({"_id": ObjectId(id)})

        if file_meta is None:
            raise HTTPException(status_code=404, detail="Image not found")

        file_id = file_meta['fileId']
        gridfs_file = fs.get(ObjectId(file_id))

        # Read file content
        file_content = gridfs_file.read()

        # Determine content type from filename or use default
        filename = file_meta.get('name', 'image')
        content_type = mimetypes.guess_type(filename)[0] or 'application/octet-stream'

        # If it's an image, use the appropriate MIME type
        if not content_type.startswith('image/'):
            # Default to image/jpeg if no proper type detected
            content_type = 'image/jpeg'

        # Return as streaming response
        return StreamingResponse(
            io.BytesIO(file_content),
            media_type=content_type,
            headers={
                "Content-Disposition": f"inline; filename={filename}"
            }
        )
    except Exception as e:
        logger.error(f"Error retrieving image {id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Error retrieving image")


@fileRoutes.get( "/{id}/download")
async def downloadModel(id: str, current_user: Annotated[UserModel, Depends(get_current_user('user'))]):


    file = db.files.find_one({"_id": ObjectId(id)})

    if file is None:
        raise HTTPException(status_code=404, detail="Model not found")



    file_id = file['fileId']
    file = fs.get(ObjectId(file_id))
    temp_file = NamedTemporaryFile(delete=False)
    temp_file.write(file.read())
    temp_file.close()
    return temp_file.name

@fileRoutes.post("")
async def upload_file(file: UploadFile = File(...), current_user: Annotated[UserModel, Depends(get_current_user('user'))] = None):
    
    md5 = calculate_md5(file.file)

    file_id = fs.put(file.file.read(), filename=file.filename, owner=current_user.id, test="test")

    #check for file in fsFiles

    existing = db.files.find_one({"md5": md5})

    if existing is not None:
        return fsFileModel(**existing).model_dump(exclude_none=True)


    newFsFile = {
         "name": file.filename,
         "md5": md5,
         "fileId": str(file_id),
         "references": []
    }

    inserted = db.files.insert_one(newFsFile)

    ret = db.files.find_one({"_id": inserted.inserted_id})

    return fsFileModel(**ret).model_dump(exclude_none=True)

@fileRoutes.delete("/{id}")
async def deleteModel(id: str, current_user: Annotated[UserModel, Depends(get_current_user('user'))]):
    
    model = db.files.find_one({"_id": ObjectId(id)})
    file_id = model['fileId']

    fs.delete(ObjectId(file_id))

    db.files.delete_one({"_id": ObjectId(id)})
    
    return




    