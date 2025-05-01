from .models import Tag, Media
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select


class MediaService:
    def __init__(self, session: AsyncSession):
        self.session = session

    
    async def list_tag(self, prefix: Optional[str] = None) -> List[Tag]:
        stmt = select(Tag)
        if prefix:
            stmt = stmt.where(Tag.name.startswith(prefix))
        result = await self.session.execute(stmt)
        return result.scalars().all()
    
    
    async def add_tags_to_media(
            session: AsyncSession,
            media_id: int,
            tag_names: List[str]
    ) -> Media:
        media = await session.get(Media, media_id)

    