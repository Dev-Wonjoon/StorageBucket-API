from sqlmodel import SQLModel, Field, BigInteger, Column, Relationship
from typing import Optional, List
from datetime import datetime
from utils.app_utils import now_kst

class MediaTag(SQLModel, table=True):
    __tablename__ = 'media_tag'
    
    media_id: Optional[int] = Field(default=None, foreign_key="media.id", primary_key=True)
    tag_id: Optional[int] = Field(default=None, foreign_key="tag.id", primary_key=True)


class Media(SQLModel, table=True):
    __tablename__ = "media"

    id: int = Field(default=None, primary_key=True)
    title: str
    filepath: str
    file_size: Optional[int] = Field(default=None, sa_column=Column(BigInteger))
    thumbnail_path: str = Field(default=None, nullable=True)
    platform_id: Optional[int] = Field(index=True, foreign_key="platform.id", nullable=False)
    owner_id: Optional[int] = Field(foreign_key="profile.owner_id", nullable=True)
    url_id: Optional[int] = Field(default=None, foreign_key="url.id", index=True, nullable=True)
    created_at: datetime = Field(default_factory=now_kst)
    updated_at: datetime = Field(default_factory=now_kst)
    
    platform: Optional["Platform"] = Relationship(back_populates="medias")
    url: Optional["Url"] = Relationship(back_populates="medias")
    profile: Optional["Profile"] = Relationship(back_populates="medias")
    tags: List["Tag"] = Relationship(back_populates="media", link_model=MediaTag)