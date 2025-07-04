from abc import ABC, abstractmethod
from pathlib import Path
from pydantic import BaseModel
from typing import Generic, Any, List, TypeVar, Optional

from utils.app_utils import uuid_generator, safe_string
from utils.image_utils import convert_to_webp
from utils.ytdlp_utils import YtOptsBuilder, VideoContainer

import asyncio, httpx, yt_dlp


def _ensure_dir(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    return path

MetaT = TypeVar("MetaT", bound=dict[str, Any] | None)

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


class Downloader(ABC, Generic[MetaT]):

    @abstractmethod
    async def download(self, url:str) -> DownloadResult: ...


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


class GenericDownloader(Downloader[MetaT], Generic[MetaT]):
    
    def __init__(
        self,
        platform: str,
        root_dir: Path,
        extractor: Optional[Extractor[MetaT]] = None,
        http_client: Optional[httpx.AsyncClient] = None,
    ) -> None:
        self.extractor = extractor
        self.platform = platform.lower()
        self.http = http_client or httpx.AsyncClient(timeout=10)
        
        self.platform_dir = _ensure_dir(root_dir.expanduser() / self.platform)
        self.thumb_dir = _ensure_dir(self.platform_dir / "thumbnails")
        
    async def download(self, url: str) -> DownloadResult[MetaT]:
        meta = (await self.extractor.extract(url)) if self.extractor else await self._probe_with_yt_dlp(url)
        
        uid = uuid_generator()
        video = await self._download_video(meta, uid)
        
        thumbnail_filename, thumbnail_filepath = await self._handle_thumbnail(
            meta.thumbnail_url, meta.title, uid
        )
        
        files = [FileInfo(filename=video.filename, filepath=video.filepath)]
        if thumbnail_filepath:
            files.append(FileInfo(filename=thumbnail_filename, filepath=thumbnail_filepath))
            
        return DownloadResult(
            title=meta.title,
            platform=self.platform,
            files=files,
            metadata=meta.metadata
        )
        
    def _build_filename(self, title: str, uid: str, ext: str) -> str:
        return f"{safe_string(title)}_{uid}.{ext}"
        
    async def _download_video(
        self,
        meta,
        uid: str,
        video_container: VideoContainer = VideoContainer.mp4,
    ) -> Path:
        dest_stem = self.platform_dir / f"{safe_string(meta.title)}_{uid}"
        
        ydl_opts = (
            YtOptsBuilder()
            .best_video_audio()
            .merge_output(video_container)
            .outtmpl(f"{dest_stem}.%(ext)s")
            .build()
        )
        
        def _run():
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([meta.video_url])
                
        await asyncio.to_thread(_run)
        filepath =  dest_stem.with_suffix(f".{meta.ext}")
        return FileInfo(filename=filepath.name, filepath=filepath)
    
    async def _handle_thumbnail(
        self, url: Optional[str], title: str, uid: str
    ) -> tuple[Optional[str], Optional[Path]]:
        if not url:
            return None, None
        data = await self._fetch_bytes(url)
        if not data:
            return None, None
        
        webp = await asyncio.to_thread(convert_to_webp, data)
        filename = self._build_filename(title, uid, "webp")
        path = self.thumb_dir / filename
        path.write_bytes(webp)
        return filename, path
        
    
    async def _fetch_bytes(self, url: str) -> Optional[bytes]:
        r = await self.http.get(url)
        return r.content if r.status_code == 200 else None
    
    async def _probe_with_yt_dlp(self, url: str) -> ExtractionResult[dict[str, Any]]:
        ydl_opts = {"quiet": True, "skip_download": True}
        
        def _probe():
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                return ydl.extract_info(url, download=False)
            
        info = await asyncio.to_thread(_probe)
        
        return ExtractionResult(
            title=info.get("title", "video"),
            video_url=info.get("url"),
            ext=info.get("ext", "mp4"),
            thumbnail_url=info.get("thumbnail"),
            metadata=info,
        )