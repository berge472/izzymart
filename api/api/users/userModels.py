from typing import Optional
from pydantic import BaseModel, Field
from api.common.pyObjectId import PyObjectId


class UserModel(BaseModel):
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias='_id')
    username: Optional[str]  = Field(default=None, example="johndoe")
    type: Optional[str]  = Field(default='user', enumerate=['user', 'apikey'])
    email: Optional[str] = Field(default=None, example="john.doe@email.com")
    role: Optional[str]  = Field(default=None, example="admin")
    password: Optional[str]  = Field(default=None, example="password")
    expires: Optional[str]  = Field(default=None, example="2022-01-01")
