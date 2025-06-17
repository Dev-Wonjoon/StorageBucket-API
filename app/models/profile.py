from typing import Optional, List
from sqlmodel import Field, SQLModel, Relationship
from datetime import datetime
from app.models.media import Media
from utils.time_utils import now_kst


class Profile(SQLModel, table=True):
    __tablename__ = "profile"

    owner_id: int = Field(default=None, index=True, primary_key=True)
    owner_name: str = Field(nullable=False)

    medias: List[Media] = Relationship(back_populates="profile")

    updated_at: datetime = Field(default_factory=now_kst)