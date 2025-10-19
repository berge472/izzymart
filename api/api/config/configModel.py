from typing import Optional
from pydantic import BaseModel, Field
from api.common.pyObjectId import PyObjectId
from enum import Enum

class registrationScheme(str,Enum):
    open = "open"                           # Open registration, anyone can create an account
    requireApproval = "requireApproval"     # Anyone can register, but must be approved by an admin before they can use the system
    none = "none"                           # No registration allowed, only admin can create accounts
    

class ConfigModel(BaseModel):
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias='_id')
    registration: registrationScheme = Field(default="requireApproval", example="none")
    secret_key: Optional[str] = Field(default=None, example="")
    algorithm: Optional[str] = Field( example="", default="HS256")

    class Config:
        json_encoders = {
            PyObjectId: str
        }
