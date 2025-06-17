from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List
from app.models.media import Media

class Url(SQLModel, table=True):
    __tablename__ = "url"

    id: Optional[int] = Field(default=None, primary_key=True)
    url: str = Field(nullable=False, unique=True)

    medias: List["Media"] = Relationship(back_populates="url")