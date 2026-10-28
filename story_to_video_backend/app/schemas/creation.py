from pydantic import BaseModel, EmailStr
from typing import Optional

class CreationCreateRequest (BaseModel):
    story_text: str
    status: Optional[str] = "pending"
    

class CreationResponse (BaseModel):
    id: int
    story_text: str
    status: Optional[str] = "pending"
    video_url: Optional[str] = None
    class Config:
        from_attributes = True