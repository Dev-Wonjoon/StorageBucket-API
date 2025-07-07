from sqlmodel.ext.asyncio.session import AsyncSession
from app.services.abstract_media_service import AbstractMediaService
from downloader.generic import GenericDownloader
from core.exception import DuplicateUrlError
from app.models.urls import Url
from sqlmodel import select
from core import settings
from downloader.models import DownloadResult


class GenericMediaService(AbstractMediaService):
    
    def __init__(self, session: AsyncSession, platform_name: str) -> None:
        self.PLATFORM_NAME = platform_name.lower()
        super().__init__(session)
        
        self.downloader = GenericDownloader(
            platform=self.PLATFORM_NAME,
            root_dir=settings.download_dir,
            extractor=self.PLATFORM_NAME,
        )
        
    async def _get_or_create_url(self, url: str):
        if (await self.session.exec(select(Url).where(Url.url == url))).first():
            raise DuplicateUrlError(url)
        
        url_obj = Url(url=url)
        self.session.add(url_obj)
        await self.session.flush()
        return url_obj
    
    async def _download(self, url: str) -> DownloadResult:
        return await self.downloader.download(url)