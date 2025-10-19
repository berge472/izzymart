from typing import List
from pydantic import  Field, BeforeValidator
from typing import Annotated



PyObjectId = Annotated[str, BeforeValidator(str)]