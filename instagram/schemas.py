from datetime import datetime
from typing import List, Optional
from sqlmodel import SQLModel
from core.models import Media

class ProfileSchema(SQLModel):
    owner_id: int
    owner_name: str
    medias: List[Media] = []

    class Config:
        from_attributes = True

class ProfileRead(SQLModel):
    owner_id: int
    owner_name: str
    media_count: int

    class Config:
        from_attributes = True