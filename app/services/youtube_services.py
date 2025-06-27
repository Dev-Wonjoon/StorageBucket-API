from fastapi import HTTPException
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from typing import Callable

from app.models.media import Media
from app.models.urls import Url
from app.services.platform_service import PlatformService
from core import settings
from downloader.base import DownloadResult
from downloader.youtube_downloader import YoutubeDownloader
from utils.time_utils import now_kst


YT_VIDEO_DIR = settings.yt_video_dir
YT_THUMBNAIL_DIR = settings.yt_thumbnail_dir


class YoutubeService:
    def __init__(
        self,
    ):
        self.downloader = YoutubeDownloader(YT_VIDEO_DIR, YT_THUMBNAIL_DIR)
        self.platform_service = PlatformService()

    async def download_and_save(self, url: str, session: AsyncSession) -> DownloadResult:
        
        existing = await session.scalar(select(Url).where(Url.url == url))
        if existing:
            return HTTPException(status_code=409, detail="이미 존재하는 URL입니다.")
        
        try:
            result: DownloadResult = await self.downloader.download(url)
            title = result.title
            files = result.files
            metadata = result.metadata
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"다운로드 중 오류가 발생했습니다: {e}")
        
        if not files:
            raise HTTPException(status_code=400, detail="다운로드된 파일이 없습니다.")
        platform = await self.platform_service.get_or_create("youtube", session)


        # URL 저장
        
        url_obj = Url(url=url)
        session.add(url_obj)
        await session.commit()
        await session.refresh(url_obj)
        
        thumbnail = None
        thumbnail_path = metadata.get("thumbnail_filepath")

        media_obj = []
        
        for file in files:
            media = Media(
                title=title,
                url_id=url_obj.id,
                platform_id=platform.id,
                thumbnail_path=str(thumbnail_path) if thumbnail_path else None,
                filepath=str(file.filepath),
                filename=file.filename,
                thumbnail_id=thumbnail.id if thumbnail else None,
                created_at=now_kst(),
            )
            session.add(media)
            media_obj.append(media)
        await session.commit()
        for media in media_obj:
            await session.refresh(media)
        
        return result