from sqlmodel import Field, Relationship, SQLModel
from typing import Optional, List
from app.models.media import MediaTag, Media

class Tag(SQLModel, table=True):
    __tablename__ = "tag"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(nullable=False, unique=True)

    media: List["Media"] = Relationship(back_populates="tags", link_model=MediaTag)