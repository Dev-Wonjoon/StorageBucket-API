from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.models.urls import Url
from core import settings
from core.exception import DuplicateUrlError
from downloader.models import DownloadResult
from downloader.plugins.instagram import InstagramDownloader

from .abstract_media_service import AbstractMediaService


class InstagramService(AbstractMediaService):
    PLATFORM_NAME = "instagram"
    
    def __init__(self, session: AsyncSession):
        super().__init__(session)
        self.downloader = InstagramDownloader(settings.download_dir / self.PLATFORM_NAME)
        
    
    async def _get_or_create_url(self, url) -> Url:
        if (await self.session.exec(select(Url).where(Url.url == url))).first():
            raise DuplicateUrlError(url)
        
        url_obj = Url(url=url)
        self.session.add(url_obj)
        await self.session.flush()
        return url_obj
    
    async def _download(self, url) -> DownloadResult:
        return await self.downloader.download(url)