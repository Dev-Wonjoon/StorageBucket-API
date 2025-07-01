import asyncio, yt_dlp, re

from typing import Any, Dict, Optional

from downloader.base import DownloadResult, FileInfo, GenericDownloader, Extractor, ExtractionResult
from utils.app_utils import uuid_generator
from utils.youtube_utils import YtOptsBuilder, VideoContainer

class SoopExtractor(Extractor[Dict[str, Any]]):
    
    def __init__(self) -> None:
        self.yt_dlp = (
            YtOptsBuilder()
            .with_extractor("soop")
            .build()
        )
        self._yt_opts["skip_download"] = True
        
    async def extract(self, url: str) -> ExtractionResult[Dict[str, Any]]:
        loop = asyncio.get_running_loop()
        
        info = await loop.run_in_executor(
            None,
            lambda: yt_dlp.YoutubeDL(self._yt_opts).extract_info(url, download=False)
        )
        
        return ExtractionResult(
            title=info.get("title", ""),
            video_url=info.get("url", ""),
            thumbnail_url=info.get("thumbnail", ""),
            ext=info.get("ext", ""),
            metadata=info
        )
        
class SoopDownloader(GenericDownloader[Dict[str, Any]]):
    PLATFORM = "soop"
    
    def __init__(self, extractor, video_dir, thumb_dir = None):
        super().__init__(SoopExtractor(), video_dir, thumb_dir)
        
    async def download(self, url: str) -> DownloadResult[Dict[str, Any]]:
        extracted = await self.extractor.extract(url)
        
        uid = uuid_generator()
        safe_title = re.sub(r"[\\/:*?\"<>|]", "_", extracted.title)
        outtmpl = str(self.video_dir / f"{safe_title}_{uid}.%(ext)s")
        
        ydl_opts = (
            YtOptsBuilder()
            .best_video_audio()
            .merge_output(VideoContainer.mp4)
            .outtmpl(str(outtmpl))
            .playlist(False)
            .build()
        )
        
        loop = asyncio.get_running_loop()
        await loop.run_in_executor(None, lambda: yt_dlp.YoutubeDL(ydl_opts).download([url]))
        
        save_files = list(self.video_dir.glob(f"{safe_title}_{uid}.*"))
        filepath = save_files[0] if save_files else None
        
        thumb_filename, thumb_filepath = await self._save_thumbnail(
            extracted.thumbnail_url, safe_title, uid
        )
        
        return DownloadResult(
            file=FileInfo(
                filename=filepath.name if filepath else None,
                path=filepath,
            ),
            thumbnail=FileInfo(
                filename=thumb_filename,
                path=thumb_filepath,
            ),
            meta=extracted.metadata,
        )