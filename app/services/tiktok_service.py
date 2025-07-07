from pathlib import Path
from typing import List, Optional

from fastapi import HTTPException
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.models.media import Media
from app.models.urls import Url
from app.services.platform_service import PlatformService
from core import settings
from downloader.generic import GenericDownloader
from downloader.models import DownloadResult, FileInfo
from utils.app_utils import now_kst



class TiktokService:
    
    def __init__(self) -> None:
        self.downloader = GenericDownloader(settings.base_dir)
        self.platform_service = PlatformService()
        
        
    async def download_and_save(
        self,
        url: str,
        session: AsyncSession
    ) -> DownloadResult:
        if await session.scalar(select(Url).where(Url.url == url)):
            raise HTTPException(status_code=409, detail="이미 저장된 URL입니다.")
        
        try:
            result: DownloadResult = await self.downloader.download(url)
        except Exception as e:
            raise HTTPException(500, f"Tiktok 다운로드 실패: {e}")
        
        if not result.files:
            raise HTTPException(400, "다운로드 된 파일이 없습니다.")
        
        platform = await self.platform_service.get_or_create("tiktok", session)
        
        url_obj = Url(url=url)
        session.add(url_obj)
        await session.commit()
        await session.refresh(url_obj)
        
        thumb_path: Optional[str] = None
        
        if result.metadata and result.metadata.get("thumbnail_filepath"):
            thumb_path = str(result.metadata["thumbnail_filepath"])
            
        media_obj: List[Media] = []
        for file in result.files:
            media = Media(
                title=result.title or file.filename,
                filepath=str(file.filepath),
                filename=file.filename,
                thumbnail_path=thumb_path,
                platform_id=platform.id,
                url_id=url_obj.id,
                created_at=now_kst()
            )
            await session.commit()
            for m in media_obj:
                await session.refresh(m)
            
            return result