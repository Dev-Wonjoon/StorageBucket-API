from typing import List, Optional
from datetime import datetime
from sqlmodel import SQLModel, Field, Relationship
from pydantic import field_validator
from .utils import now_kst
from youtube.models import Youtube

class MediaTag(SQLModel, table=True):
    __tablename__ = 'media_tag'
    
    media_id: Optional[int] = Field(default=None, foreign_key="media.id", primary_key=True)
    tag_id: Optional[int] = Field(default=None, foreign_key="tag.id", primary_key=True)



class Platform(SQLModel, table=True):
    __tablename__ = "platform"

    id: int = Field(default=None, primary_key=True)
    name: str = Field(nullable=False, unique=True)

    medias: List["Media"] = Relationship(back_populates="platform")

    @field_validator("name")
    def validate_name_alpha_lower(cls, v: str) -> str:
        if not v.isalpha():
            raise ValueError("플랫폼 명은 영어만 가능합니다.")
        return v.lower()


class Media(SQLModel, table=True):
    __tablename__ = "media"

    id: int = Field(default=None, primary_key=True)
    title: str
    filepath: str
    created_at: datetime = Field(default_factory=now_kst)

    thumbnail_id: Optional[int] = Field(foreign_key="thumbnail.id", nullable=True)
    platform_id: Optional[int] = Field(index=True, foreign_key="platform.id", nullable=False)
    owner_id: Optional[int] = Field(foreign_key="profile.owner_id", nullable=True)
    url_id: Optional[int] = Field(default=None, foreign_key="url.id", index=True, nullable=True)
    
    platform: Optional[Platform] = Relationship(back_populates="medias")
    thumbnail: Optional["Thumbnail"] = Relationship(back_populates="thumbnail", sa_relationship_kwargs={"uselist": False})
    url: Optional["Url"] = Relationship(back_populates="medias")
    profile: Optional["Profile"] = Relationship(back_populates="medias")
    tags: List["Tag"] = Relationship(back_populates="media", link_model=MediaTag)


class Thumbnail(SQLModel, table=True):
    __tablename__ = "thumbnail"

    id: Optional[int] = Field(default=None, primary_key=True)
    filename: str = Field(default=None, nullable=False)
    filepath: str = Field(default=None, nullable=False)

    media: Optional["Media"] = Relationship(
        back_populates="thumbnail",
        sa_relationship_kwargs={"uselist": False},
    )



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