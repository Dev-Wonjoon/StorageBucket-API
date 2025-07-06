from pathlib import Path
from typing import Any, Dict, Generic, List, Optional, TypeVar
from pydantic import BaseModel

MetaT = TypeVar("MetaT", bound=Optional[Dict[str, Any]])


class FileInfo(BaseModel):
    filename: str
    filepath: Path
    
    model_config = {"json_encoders": {Path: str}, "frozen": True}
    
    
class DownloadResult(BaseModel, Generic[MetaT]):
    title: Optional[str]
    platform: str
    files: List[FileInfo]
    metadata: MetaT = None
    
    model_config = {"json_encoders": {Path: str}}
    

class ExtractionResult(Generic[MetaT]):
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