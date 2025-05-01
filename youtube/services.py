from core.models import Url, Media
from core.utils import now_kst
from downloader.youtube_downloader import YoutubeDownloader
from downloader.base import DownloadResult
from fastapi import HTTPException
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

class YoutubeService:
    def __init__(self):
        self.downloader = YoutubeDownloader()

    
    async def download_and_save(self, url: str, session: AsyncSession) -> DownloadResult:
        existing = await session.scalar(select(Url).where(Url.url == url))

        if existing:
            return HTTPException(
                status_code=409,
                detail="이미 존재하는 URL입니다."
            )
        
        try:
            result = await self.downloader.download(url)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Youtube 다운로드 실패 {e}")
        
        url_obj = Url(
            url=url,
        )

        session.add(url_obj)
        await session.flush()

        for file_info in result["files"]:
            media = Media(
                url_id=url_obj.id,
                platform=result["platform"].value,
                title=file_info["filename"],
                filepath=file_info["filepath"],
                created_at=now_kst()
            )
            session.add(media)
        await session.commit()
        return result
    
