from abc import ABC, abstractmethod
from sqlalchemy.ext.asyncio import AsyncSession
from typing import TypedDict, NotRequired, Any, List, Dict
from enum import Enum


class FileInfo(TypedDict):
    filepath: str
    filename: str


class Platform(Enum):
    INSTAGRAM = "instagram"
    YOUTUBE = "youtube"
    LOCAL = "local"


class DownloadResult(TypedDict, total=False):
    
    platform: Platform
    files: List[FileInfo]
    metadata = NotRequired[Dict[str, Any]]



class Downloader(ABC):

    @abstractmethod
    async def download(
        self, url:str, session: AsyncSession
    ) -> DownloadResult: ...