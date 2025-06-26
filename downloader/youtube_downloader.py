import asyncio
import yt_dlp
import httpx
import uuid

from pathlib import Path
from typing import Callable, Optional, Any

from downloader.base import Downloader, FileInfo, DownloadResult
from utils.youtube_utils import YtOptsBuilder, VideoContainer, VideoCodec, AudioCodec, AudioQuality
from utils.image_utils import convert_to_webp

RegDomainFn = Callable[[str], str]

class YoutubeDownloader(Downloader):
    
    def __init__(
        self,
        video_dir: Path,
        reg_domain: RegDomainFn,
        thumb_dir: Path,
        http_client: Optional[httpx.AsyncClient] = None
    ) -> None:
        self.video_dir = Path(video_dir).expanduser()
        self.thumb_dir = Path(thumb_dir or (video_dir / "thumbnails")).expanduser()
        
        self.extractor = RegDomainFn
        
        self.video_dir.mkdir(parents=True, exist_ok=True)
        self.thumb_dir.mkdir(parents=True, exist_ok=True)

    async def thumbnail_download(self, url: str):
        async with httpx.AsyncClient(timeout=10) as client:
            r = await client.get(url)
            if r.status_code != 200:
                return None
        return await asyncio.to_thread(convert_to_webp, r.content)


    async def download(self, url: str) -> DownloadResult:

        unique_id = uuid.uuid4().hex[:8]

        ydl_opts = {
            YtOptsBuilder()
            .best_video_audio()
            .outtmpl(self.video_dir / f"%(title)s_{unique_id}.%(ext)s")
            .merge_output(VideoContainer.mp4)
            .build()
        }

        def _download():
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                return ydl.extract_info(url, download=True)
        
        info = await asyncio.to_thread(_download)
        title = f"{info['title']}_{unique_id}"
        filename = f"{title}.{info.get('ext', 'mp4')}"
        filepath = self.video_dir / filename

        thumbnail_url = info.get("thumbnail")
        thumbnail_filename = None
        thumbnail_filepath = None
        if thumbnail_url:
            content = await self.thumbnail_download(thumbnail_url)
            if content:
                thumbnail_filename = f"{title}.jpg"
                thumbnail_filepath = self.thumb_dir / thumbnail_filename
                with open(thumbnail_filepath, "wb") as f:
                    f.write(content)

        return DownloadResult({
            "platform": self.extractor(url),
            "title": info["title"],
            "files": [FileInfo(filename=filename, filepath=filepath)],
            "metadata": {
                "thumbnail_filename": thumbnail_filename,
                "thumbnail_filepath": thumbnail_filepath
            }
        })
    
    async def download_audio(self, url: str) -> DownloadResult:
        unique_id = uuid.uuid4().hex[:8]
        ydl_opts = {
            YtOptsBuilder()
            .best_audio()
            .outtmpl(self.video_dir / f"%(title)s_{unique_id}.%(ext)s")
            .build()
        }
        
        def _extract():
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                return ydl.extract_info(url, download=True)
        
        info = await asyncio.to_thread(_extract)
        filename = f"{info['title']}_{unique_id}.{info.get('ext' or 'mp3')}"
        filepath = self.video_dir / filename
        
        thumbnail_url = info.get("thumbnail")
        thumbnail_filename = None
        thumbnail_filepath = None
        if thumbnail_url:
            content = await self.thumbnail_download(thumbnail_url)
            if content:
                thumbnail_filename = f"{info['title']}.jpg"
                thumbnail_filepath = self.thumb_dir / thumbnail_filename
                with open(thumbnail_filepath, "wb") as f:
                    f.write(content)
        return DownloadResult({
            "platform": self.extractor(url),
            "title": info["title"],
            "files": [FileInfo(filename=filename, filepath=filepath)],
            "metadata": {
                "thumbnail_filename": thumbnail_filename,
                "thumbnail_filepath": thumbnail_filepath
            }
        })