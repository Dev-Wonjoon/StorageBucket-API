import asyncio, re, yt_dlp

from pathlib import Path
from typing import Dict, Any, Optional

from downloader.base import DownloadResult, Extractor, ExtractionResult, FileInfo, GenericDownloader
from utils.app_utils import uuid_generator, safe_string
from utils.image_utils import convert_to_webp
from utils.youtube_utils import YtOptsBuilder, VideoContainer


class XExtractor(Extractor[Dict[str, Any]]):
    def __init__(
        self,
        *,
        cookies: Optional[str] = None,
    ) -> None:
        self._yt_opts = (
            YtOptsBuilder()
            .with_extractor("tiwtter")
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
            title=info.get("title", "") or info.get("id", ""),
            video_url=info.get("url"),
            ext=info.get("ext", "mp4"),
            thumbnail_url=info.get("thumbnail"),
            metadata=info,
        )
        
        
class XDownloader(GenericDownloader[Dict[str, Any]]):
    PLATFORM = "x"
    
    def __init__(self, extractor, platform_dir, thumb_dir = None, * cookies: Optional[str]):
        
        extractor = XExtractor(
            cookies=cookies
        )
        
        super().__init__(extractor, platform_dir, thumb_dir)
        
    
    async def download(self, url: str) -> DownloadResult[Dict[str, Any]]:
        extracted = await self.extractor.extract(url)
        
        uid = uuid_generator()
        safe_title = safe_string(extracted.title)
        outtmpl = str(self.platform_dir / f"{safe_title}_{uid}.%(ext)s")
        
        ydl_opts = (
            YtOptsBuilder()
            .with_extractor("twitter")
            .best_video_audio()
            .merge_output(VideoContainer.mp4)
            .outtmpl(outtmpl)
            .playlist(False)
            .build()
        )
        
        for key in ("cookies"):
            if key in self.extractor._yt_opts:
                ydl_opts[key] = self.extractor._yt_opts[key]
                
        loop = asyncio.get_running_loop()
        await loop.run_in_executor(
            None,
            lambda: yt_dlp.YoutubeDL(ydl_opts).download(url),
        )
        
        saved_files = list()