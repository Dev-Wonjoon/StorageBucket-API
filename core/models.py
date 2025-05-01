from typing import List, Optional
from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime
from .utils import now_kst


class MediaTag(SQLModel, table=True):
    __tablename__ = 'media_tag'
    
    media_id: Optional[int] = Field(default=None, foreign_key="media.id", primary_key=True)
    tag_id: Optional[int] = Field(default=None, foreign_key="tag.id", primary_key=True)


class Media(SQLModel, table=True):
    __tablename__ = "media"

    id: int = Field(default=None, primary_key=True)
    platform: str = Field(index=True)
    title: str
    filepath: str
    created_at: datetime = Field(default_factory=now_kst)

    owner_id: int = Field(foreign_key="profile.owner_id", nullable=True)
    url_id: Optional[int] = Field(default=None, foreign_key="url.id", index=True, nullable=True)
    
    
    url: Optional["Url"] = Relationship(back_populates="medias")
    profile: "Profile" = Relationship(back_populates="medias")
    tags: List["Tag"] = Relationship(back_populates="media", link_model=MediaTag)


class Thumbnail(SQLModel, table=True):
    __tablename__ = "thumbnail"

    id: Optional[int] = Field(default=None, primary_key=True)
    filepath: str = Field(default=None, nullable=False)



class Tag(SQLModel, table=True):
    __tablename__ = "tag"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(nullable=False, unique=True)

    media: List["Media"] = Relationship(back_populates="tags", link_model=MediaTag)


class Url(SQLModel, table=True):
    __tablename__ = "url"

    id: Optional[int] = Field(default=None, primary_key=True)
    url: str = Field(nullable=False, unique=True)

    medias: List["Media"] = Relationship(back_populates="url")