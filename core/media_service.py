from typing import List
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from .models import Media
from core.db import get_session

class MediaService:
    async def list_media(session: AsyncSession) -> List[Media]:
        stmt = select(Media)
        result = await session.exec(stmt)
        return result.all()
    

    