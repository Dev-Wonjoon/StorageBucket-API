from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.models.urls import Url
from app.services.abstract_media_service import AbstractMediaService
from core.exception import DuplicateUrlError
from core.config import Settings
from downloader.interfaces import DownloadResult
from downloader.generic import GenericDownloader


class YoutubeService(AbstractMediaService):
    
    PLATFORM_NAME = "youtube"
    
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session)
        self.downloader = GenericDownloader(platform=self.PLATFORM_NAME, root_dir=Settings().base_dir, extractor=None)
        
        
    async def _get_or_create_url(self, url):
        result = (await self.session.exec(
            select(Url).where(Url.url == url)
        )).first()
        
        if result:
            raise DuplicateUrlError(url)
        
        url_obj = Url(url=url)
        self.session.add(url_obj)
        await self.session.flush()
        return url_obj
    
    async def _download(self, url) -> DownloadResult:
        return await self.downloader.download(url)
        