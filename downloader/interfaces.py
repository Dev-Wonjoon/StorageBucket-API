from abc import ABC, abstractmethod
from typing import Generic, TypeVar, Optional, Dict, Any
from .models import DownloadResult, ExtractionResult

MetaT = TypeVar("MetaT", bound=Optional[Dict[str, Any]])


class Downloader(ABC, Generic[MetaT]):
    @abstractmethod
    async def download(self, url: str) -> DownloadResult[MetaT]:
        ...

class Extractor(ABC, Generic[MetaT]):
    @abstractmethod
    async def extract(self, url: str) -> ExtractionResult[MetaT]:
        ...