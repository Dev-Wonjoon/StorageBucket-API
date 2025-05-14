from typing import List, Optional
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from .models import Media
from core.db import get_session

class MediaService:
    async def list_media(session: AsyncSession) -> List[Media]:
        stmt = select(Media)
        result = await session.exec(stmt)
        return result.all()
    
    async def get_medialist_by_cursor(
            cursor: Optional[int],
            limit: int,
            session: AsyncSession
    ) -> List[Media]:
        """
        cursor: 마지막으로 받은 Media.id (없으면 처음부터)
        limit: 한 번에 가져올 개수
        """
        stmt = select(Media).order_by(Media.id)
        if cursor is not None:
            stmt = stmt.where(Media.id > cursor)
        stmt = stmt.limit(limit)

        result = await session.exec(stmt)
        return result.all()

    