from collections.abc import Sequence
from sqlmodel.ext.asyncio.session import AsyncSession
from app.models.media import Media
from downloader.base import FileInfo
from utils.app_utils import now_kst

class MediaRepository:
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def add_medias(
        self,
        *,
        platform_id: int,
        files: Sequence[FileInfo],
        url_id: int,
        caption: str | None = None,
        owner_id: int | None = None,
        owner_name: str | None = None,
    ) -> list[Media]:
        now = now_kst()
        objs = [
            Media(
                platform_id=platform_id,
                filepath=str(f.filepath),
                filename=f.filename,
                title=caption or f.filename,
                owner_id=owner_id,
                owner_name=owner_name,
                url_id=url_id,
                created_at=now,
            )
            for f in files
        ]
        self.session.add_all(objs)
        
        await self.session.flush()
        return objs
        