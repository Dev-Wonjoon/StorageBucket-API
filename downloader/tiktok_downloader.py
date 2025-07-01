import asyncio, re, yt_dlp

from pathlib import Path
from typing import Any, Dict, Optional

from downloader.base import FileInfo, DownloadResult, GenericDownloader, Extractor, ExtractionResult
from utils.app_utils import uuid_generator
from utils.image_utils import convert_to_webp
from utils.youtube_utils import YtOptsBuilder, VideoContainer


class TiktokExtractor(Extractor[Dict[str, Any]]):
    
    def __init__(self) -> None:
        self._yt_opts = (
            YtOptsBuilder()
            .with_extractor("tiktok")
            .build()
        )
        self._yt_opts("skip_download") = True
        
    async def extract(self, url: str) -> ExtractionResult[Dict[str, Any]]:
        loop = asyncio.get_running_loop()
        info: Dict[str, Any] = await loop.run_in_executor(
            None,
            lambda: yt_dlp.YoutubeDL(self._yt_opts).extract_info(url, download=False)
        )
        
        return ExtractionResult(
            title=info.get("title", ""),
            video_url=info.get("url"),
            ext=info.get("ext", "mp4"),
            thumbnail_url=info.get("thumbnail"),
            metadata=info,
        )
        

class TiktokDownloader(GenericDownloader[Dict[str, Any]]):
    PLATFORM = "Tiktok"
    
    def __init__(self, extractor, video_dir, thumb_dir = None):
        super().__init__(extractor, video_dir, thumb_dir)
        
    async def download(self, url: str) -> DownloadResult[Dict[str, Any]]:
        extracted = await self.extractor.extract(url)
        
        uid = uuid_generator()
        safe_title = re.sub(r'[\\/:*?"<>|]', "_", extracted.title)
        outtmpl = self.video_dir / f"{safe_title}_{uid}.%(ext)s"
        
        ydl_opts = (
            YtOptsBuilder()
            .best_video_audio()
            .merge_output(VideoContainer.mp4)
            .outtmpl(str(outtmpl))
            .playlist(False)
            .build()
        )
        
        loop = asyncio.get_running_loop()
        await loop.run_in_executor(
            None,
            lambda: yt_dlp.YoutubeDL(ydl_opts).download(url)
        )
        
        saved_files = list(self.video_dir.glob(f"{safe_title}_{uid}.*"))
        file_path = saved_files[0] if saved_files else None
        
        thumb_filename, thumb_path = await self._save_thumbnail(
            extracted.thumbnail_url, safe_title, uid)
        
        
        return DownloadResult(
            file=FileInfo(
                filename=file_path.name if file_path else None,
                path=file_path,
            ),
            thumbnail=FileInfo(
                filename=thumb_filename,
                path=thumb_path,
            ),
            meta=extracted.metadata,
        )