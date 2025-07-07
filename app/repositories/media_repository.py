from collections.abc import Sequence
from sqlmodel.ext.asyncio.session import AsyncSession
from app.models.media import Media
from downloader.models import FileInfo
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
        common = {
            "platform_id": platform_id,
            "url_id": url_id,
            "created_at": now
        }
        optional = {k: v for k, v in{
            "owner_id": owner_id,
            "owner_name": owner_name,
            "caption": caption
        }.items() if v is not None}
        
        objs = [
            Media(
                **common,
                **optional,
                filepath=str(f.filepath),
                filename=f.filename,
                filesize=f.filesize,
                title=caption or f.filename,
            )
            for f in files
        ]
        self.session.add_all(objs)
        
        await self.session.flush()
        return objs
        