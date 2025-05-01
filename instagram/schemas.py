from datetime import datetime
from typing import List, Optional
from sqlmodel import SQLModel
from core.schemas import MediaSchema

class ProfileSchema(SQLModel):
    owner_id: int
    owner_name: str
    medias: List[MediaSchema] = []

    class Config:
        from_attributes = True

class ProfileRead(SQLModel):
    owner_id: int
    owner_name: str
    media_count: int

    class Config:
        from_attributes = True