from datetime import datetime
from sqlmodel import SQLModel


class MediaSchema(SQLModel):
    id: int
    platform: str
    title: str
    filepath: str
    created_at: datetime

    class Config:
        from_attributes = True