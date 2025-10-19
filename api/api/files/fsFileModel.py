from typing import Optional, List, Dict
from pydantic import BaseModel, Field
from api.common.pyObjectId import PyObjectId




class fsFileModel(BaseModel):
    """ 
        fsFileModels point to files in the gridFS collection and include metadata about the file including the md5 hash and which other documents reference the file.

        This is used to prevent orphance and duplicate files in the gridFS collection.
    """


    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias='_id')
    name: str = Field( example="mode1", description="Name of the mode")
    md5: str = Field( example="md5", description="md5 of the file")
    fileId: str = Field( example="fileId", description="Id of the file")
    references: List[str] = Field( example=["ref1","ref2"], description="List of IDs of the references")
