from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.models.urls import Url
from app.services.base_media_service import BaseMediaService
from core.exception import DuplicateUrlError
from core.config import Settings
from downloader.base import DownloadResult
from downloader.youtube_downloader import YoutubeDownloader


class YoutubeService(BaseMediaService):
    
    PLATFORM_NAME = "youtube"
    
    def __init__(self, session):
        super().__init__(session)
        self.downloader = YoutubeDownloader(Settings().base_dir)