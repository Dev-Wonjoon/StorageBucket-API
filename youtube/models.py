from typing import Optional, List
from sqlmodel import SQLModel, Field, Relationship
from core.models import Thumbnail, Media


class Youtube(SQLModel, table=True):
    __tablename__ = "youtube"

    id: Optional[int] = Field(default=None, primary_key=True)
    thumbnail_id: Optional[int] = Field(default=None, foreign_key="thumbnail.id", index=True)
    media_id: Optional[int] = Field(default=None, foreign_key="media.id", index=True)

    thumbnail: Optional["Thumbnail"] = Relationship(back_populates="youtube", sa_relationship_kwargs={
        "uselist": False,
    })
    media: Optional["Media"] = Relationship(back_populates="youtube", sa_relationship_kwargs={
        "uselist": False
    })