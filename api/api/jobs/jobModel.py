from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class jobPromptModel(BaseModel):
    text: Optional[str] = Field(title="Prompt", description="Prompt for the job when waiting for input", default=None)
    responses: Optional[List[str]] = Field(title="Responses", description="List of responses to the prompt", default=None)
    ctx: Optional[Any] = Field(title="Context", description="Context for the job", default=None)


class jobStatusModel(BaseModel):
    uuid: Optional[str] = Field(title="UUID", description="Unique identifier for the job", default=None)
    totalTasks: Optional[int] = Field(title="Total Tasks", description="Total number of tasks in the job", default=None)
    completedTasks: Optional[int] = Field(title="Completed Tasks", description="Number of tasks completed", default=None)
    status: Optional[str] = Field(title="Status", description="Status of the job", default=None)
    prompt: Optional[jobPromptModel] = Field(title="Prompt", description="Prompt for the job", default=None)
    