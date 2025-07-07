from pathlib import Path
from typing import Any, Dict, Generic, List, Optional, TypeVar
from pydantic import BaseModel, field_validator

MetaT = TypeVar("MetaT", bound=Optional[Dict[str, Any]])


class FileInfo(BaseModel):
    filename: str
    filepath: Path
    filesize: int | None = None
    
    @field_validator("filesize", mode="before", check_fields=False)
    @classmethod
    def auto_size(cls, v, values):
        if v is not None:
            return v
        fp: Path | None = values.get("filepath")
        if fp and fp.exists():
            return fp.stat().st_size
        return None
    
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