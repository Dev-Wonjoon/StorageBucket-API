import asyncio, yt_dlp
from typing import Dict, Any
from utils.ytdlp_utils import YtOptsBuilder
from .models import ExtractionResult
from downloader.interfaces import Extractor


class GenericExtractor(Extractor[Dict[str, Any]]):
    def __init__(self, platform_name: str) -> None:
        ydl_opts = (
            YtOptsBuilder().with_extractor(platform_name).build()
        )
        ydl_opts["skip_download"] = True
        ydl_opts.update(
            {
                "extractor_args": {platform_name: []}
            }
        )
        self._opts = ydl_opts
        
    async def extract(self, url: str) -> ExtractionResult[Dict[str, Any]]:
        def _probe() -> Dict[str, Any]:
            with yt_dlp.YoutubeDL(self._opts) as ydl:
                return ydl.extract_info(url, download=False)
        
        info = await asyncio.to_thread(_probe)
        
        return ExtractionResult(
            title=info.get("title") or "video",
            video_url=url,
            ext=info.get("ext", "mp4"),
            thumbnail_url=info.get("thumbnail"),
            metadata=info,
        )