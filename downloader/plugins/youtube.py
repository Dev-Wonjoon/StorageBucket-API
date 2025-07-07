import asyncio
import yt_dlp
import httpx

from pathlib import Path
from typing import Optional

from downloader.models import FileInfo, DownloadResult
from downloader.interfaces import Downloader
from utils.app_utils import uuid_generator
from utils.image_utils import convert_to_webp
from utils.ytdlp_utils import YtOptsBuilder, VideoContainer

class YoutubeDownloader(Downloader):
    PLATFORM = "youtube"
    
    def __init__(
        self,
        video_dir: Path,
        thumb_dir: Optional[Path] = None,
    ) -> None:
        self.video_dir = video_dir.expanduser()
        self.thumb_dir = (thumb_dir or (video_dir / "thumbnails")).expanduser()
        
        self.video_dir.mkdir(parents=True, exist_ok=True)
        self.thumb_dir.mkdir(parents=True, exist_ok=True)

    async def _fetch_bytes(self, url: str) -> Optional[bytes]:
        async with httpx.AsyncClient() as client:
            r = await client.get(url)
            if r.status_code == 200:
                return r.content
        return None
    async def thumbnail_download(self, url: str):
        data = await self._fetch_bytes(url)
        if data:
            return await asyncio.to_thread(convert_to_webp, data)
        return None


    async def download(self, url: str) -> DownloadResult:

        unique_id = uuid_generator()

        ydl_opts = (
            YtOptsBuilder()
            .best_video_audio()
            .outtmpl(self.video_dir / f"%(title)s_{unique_id}.%(ext)s")
            .merge_output(VideoContainer.mp4)
            .build()
        )
        
        info = await asyncio.to_thread(
            lambda: yt_dlp.YoutubeDL(ydl_opts).extract_info(url, download=True))
        title = f"{info['title']}_{unique_id}"
        filename = f"{title}.{info.get('ext', 'mp4')}"
        filepath = self.video_dir / filename

        thumbnail_filename: Optional[str] = None
        thumbnail_filepath: Optional[Path] = None
        if (thumbnail_url := info.get('thumbnail')):
            if (thumb_bytes := await self.thumbnail_download(thumbnail_url)):
                thumbnail_filename = f"{title}.webp"
                thumbnail_filepath = self.thumb_dir / thumbnail_filename
                thumbnail_filepath.write_bytes(thumb_bytes)

        return DownloadResult(
            platform= self.PLATFORM,
            title=info["title"],
            files= [FileInfo(filename=filename, filepath=filepath)],
            metadata= {
                "thumbnail_filename": thumbnail_filename,
                "thumbnail_filepath": thumbnail_filepath
            })
    
    async def download_audio(self, url: str) -> DownloadResult:
        unique_id = uuid_generator()
        ydl_opts = (
            YtOptsBuilder()
            .best_audio()
            .outtmpl(self.video_dir / f"%(title)s_{unique_id}.%(ext)s")
            .build()
        )
        
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
        return DownloadResult(
            platform= self.PLATFORM,
            title=info["title"],
            files=[FileInfo(filename=filename, filepath=filepath)],
            metadata= {
                "thumbnail_filename": thumbnail_filename,
                "thumbnail_filepath": thumbnail_filepath
            })