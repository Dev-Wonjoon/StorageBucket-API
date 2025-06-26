from abc import ABC, abstractmethod
from pathlib import Path
from typing import Generic, Any, List, Dict, TypeVar

from pydantic import BaseModel, Field


class FileInfo(BaseModel):
    filename: str
    filepath: Path
    
    model_config = {
        "json_encoders": {Path: str},
        "frozen": True,
    }


MetaT = TypeVar("MetaT", bound=dict[str, Any] | None)

class DownloadResult(BaseModel, Generic[MetaT]):
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