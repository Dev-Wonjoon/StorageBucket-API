from abc import ABC, abstractmethod
from sqlalchemy.ext.asyncio import AsyncSession
from typing import TypedDict, NotRequired, Any, List, Dict
from enum import Enum
from typing_extensions import NotRequired


class FileInfo(TypedDict):
    filename: str
    filepath: str


class DownloadResult(TypedDict):
    platform: str
    files: List[FileInfo]
    metadata: NotRequired[Dict[str, Any]]


class Downloader(ABC):

    @abstractmethod
    async def download(
        self, url:str, session: AsyncSession
    ) -> DownloadResult: ...