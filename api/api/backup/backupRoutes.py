from fastapi import status , Depends, File, UploadFile
from fastapi.responses import FileResponse
from typing import Annotated, Optional
from util.authUtil import get_current_user
from fastapi import APIRouter, BackgroundTasks
from config.db import db
from api.users.userModels import UserModel
import os
import datetime
from util.log import logger

backup_dir = os.environ.get("BACKUP_DIR", "data/backup")
mongo_host = os.environ.get("MONGO_HOST", "localhost")
mongo_db_name = os.environ.get("MONGO_DB_NAME", "app")

backupRoutes = APIRouter()

async def assertBackupDir():
    if not os.path.exists(backup_dir):
        os.makedirs(backup_dir)


log = logger(__name__)


@backupRoutes.get("")
async def getAll(current_user: Annotated[UserModel, Depends(get_current_user('user'))]):

    await assertBackupDir()

    ret = []


    backups = os.listdir(backup_dir)

    for backup in backups:
        stats = os.stat(f"{backup_dir}/{backup}")
        ret.append({
            "name": backup,
            "size": stats.st_size,
            "date": datetime.datetime.fromtimestamp(stats.st_ctime).isoformat()
        })

    return ret

@backupRoutes.post("")
async def createBackup(current_user: Annotated[UserModel, Depends(get_current_user('user'))]):

    if current_user.role != "admin":
        return {"status": "error", "message": "Only admin can create backup"}

    await assertBackupDir()
    fileName = f'{mongo_db_name}-backup-{datetime.datetime.now().strftime("%Y%m%d_%H%M%S")}.gz'
    log.info(f"Create backup file {fileName} in {backup_dir}")
    log.info(f"mongodump --uri=mongodb://{mongo_host}:27017/{mongo_db_name} --gzip")
    os.system(f"mongodump --uri=mongodb://{mongo_host}:27017/{mongo_db_name} --archive={backup_dir}/{fileName} --gzip")
    return fileName

@backupRoutes.delete("/{fileName}")
async def deleteBackup(fileName: str, current_user: Annotated[UserModel, Depends(get_current_user('admin'))]):


    await assertBackupDir()
    log.info(f"Delete backup file {fileName} in {backup_dir}")
    os.remove(f"{backup_dir}/{fileName}")
    return {"status": "ok"}

@backupRoutes.get("/{fileName}/download")
async def downloadBackup(fileName: str, current_user: Annotated[UserModel, Depends(get_current_user('admin'))]):

    await assertBackupDir()
    return FileResponse(f"{backup_dir}/{fileName}", filename=fileName)

@backupRoutes.post("/restore/{fileName}")
async def restoreBackup(fileName: str, clearData: bool = True, current_user: Annotated[UserModel, Depends(get_current_user('admin'))] = None):


    if clearData:
        log.info(f"Clearing data")
        db.drop_collection("users")
        db.drop_collection("fs.files")
        db.drop_collection("fs.chunks")

    await assertBackupDir()
    log.info(f"mongorestore --uri=mongodb://{mongo_host}:27017/{mongo_db_name} --gzip --archive={backup_dir}/{fileName}")
    os.system(f"mongorestore --uri=mongodb://{mongo_host}:27017/{mongo_db_name} --gzip --archive={backup_dir}/{fileName}")
    return {"status": "ok"}

@backupRoutes.post("/restore")
async def uploadBackup(file: UploadFile = File(...), clearData: bool = True, current_user: Annotated[UserModel, Depends(get_current_user('admin'))] = None):

    await assertBackupDir()
    contents =  file.file.read()
    fileName = file.filename
    with open(f"{backup_dir}/{fileName}", "wb") as f:
        f.write(contents)

    if clearData:
        log.info(f"Clearing data")
        db.drop_collection("users")
        db.drop_collection("fs.files")
        db.drop_collection("fs.chunks")

    log.info(f"mongorestore --uri=mongodb://{mongo_host}:27017/{mongo_db_name} --gzip --archive={backup_dir}/{fileName}")
    os.system(f"mongorestore --uri=mongodb://{mongo_host}:27017/{mongo_db_name} --gzip --archive={backup_dir}/{fileName}")


    return {"status": "ok"}