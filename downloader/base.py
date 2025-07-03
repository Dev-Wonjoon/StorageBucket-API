from abc import ABC, abstractmethod
from pathlib import Path
from pydantic import BaseModel
from typing import Generic, Any, List, TypeVar, Optional

from utils.app_utils import uuid_generator, safe_string
from utils.image_utils import convert_to_webp

import asyncio, httpx, re


MetaT = TypeVar("MetaT", bound=dict[str, Any] | None)

class FileInfo(BaseModel):
    filename: str
    filepath: Path
    
    model_config = {
        "json_encoders": {Path: str},
        "frozen": True,
    }

class DownloadResult(BaseModel, Generic[MetaT]):
    title: Optional[str]
    platform: str
    files: List[FileInfo]
    metadata: MetaT = None
    
    model_config = {
        "json_encoders": {Path: str},
    }


class Downloader(ABC, Generic[MetaT]):

    @abstractmethod
    async def download(
        self, url:str
    ) -> DownloadResult: ...


class ExtractionResult(Generic[MetaT]):
    """다운로드 전, 메타데이터까지 얻어오는 결과"""
    def __init__(
        self,
        title: str,
        video_url: str,
        ext: str,
        thumbnail_url: Optional[str] = None,
        metadata: MetaT = None
    ):
        self.title = title
        self.video_url = video_url
        self.ext = ext
        self.thumbnail_url = thumbnail_url
        self.metadata = metadata or {}
        

class Extractor(ABC, Generic[MetaT]):
    
    @abstractmethod
    async def extract(self, url: str) -> ExtractionResult[MetaT]:
        ...


class GenericDownloader(Generic[MetaT]):
    PLATFORM: str = "generic"
    
    def __init__(
        self,
        extractor: Extractor[MetaT],
        root_dir: Path,
    ):
        self.extractor = extractor
        self.platform_dir = (root_dir / self.PLATFORM).expanduser()
        self.thumb_dir = self.platform_dir / "thumbnails"
        self.platform_dir.mkdir(parents=True, exist_ok=True)
        self.thumb_dir.mkdir(parents=True, exist_ok=True)
        
    async def _fetch_bytes(self, url: str) -> Optional[bytes]:
        async with httpx.AsyncClient() as client:
            r = await client.get(url, timeout=10)
            if r.status_code == 200:
                return r.content
        return None
    
    async def _save_thumbnail(self, url: str, title: str, uid: str) -> tuple[Optional[str], Optional[Path]]:
        if not url:
            return None, None
        data = await self._fetch_bytes(url)
        if not data:
            return None, None
        webp = await asyncio.to_thread(convert_to_webp, data)
        safe_title = safe_string(title)
        filename = f"{safe_title}_{uid}.webp"
        filepath = self.thumb_dir / filename
        filepath.write_bytes(webp)
        
        return filename, filepath
    
        
    
    async def download(self, url: str) -> DownloadResult[MetaT]:
        extracted: ExtractionResult[MetaT] = await self.extractor.extract(url)
        uid = uuid_generator()
        title = f"{extracted.title}_{uid}"