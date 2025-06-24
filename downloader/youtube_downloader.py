import asyncio
import os
import yt_dlp
import httpx
import uuid
from PIL import Image
from io import BytesIO
from core import settings
from downloader.base import Downloader, FileInfo, Platform, DownloadResult

YT_VIDEO_DIR = settings.yt_video_dir
YT_TUHMBNAIL_DIR = settings.yt_thumbnail_dir

class YoutubeDownloader(Downloader):

    async def thumbnail_download(self, url: str):
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.get(url)
            resp.raise_for_status()
            content = resp.content()
        return await asyncio.to_thread(self._convert_to_webp, content)
    
    def _convert_to_webp(self, origin_bytes: bytes) -> bytes:
        img = Image.open(BytesIO(origin_bytes)).convert("RGB")
        buf = BytesIO()
        img.save(buf, format="WEBP", quality=85, optimize=True, method=3)
        return buf.getvalue()


    async def download(self, url: str) -> DownloadResult:
        dest = os.path.join(YT_VIDEO_DIR)
        thumbnail_dest = os.path.join(YT_TUHMBNAIL_DIR, "thumbnails")
        os.makedirs(dest, exist_ok=True)
        os.makedirs(thumbnail_dest, exist_ok=True)

        unique_id = uuid.uuid4().hex[:8]

        ydl_opts = {
            "format": "bestvideo+bestaudio/best",
            "outtmpl": os.path.join(dest, f"%(title)s_{unique_id}.%(ext)s"),
            "quiet": True,
            "merge_output_format": "mp4"
        }

        def _download():
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                return info
        
        info = await asyncio.to_thread(_download)
        filename = f"{info['title']}_{unique_id}.{info.get('ext', 'mp4')}"
        filepath = os.path.join(dest, filename)

        thumbnail_url = info.get("thumbnail")
        thumbnail_filename = None
        thumbnail_filepath = None
        if thumbnail_url:
            content = await self.thumbnail_download(thumbnail_url)
            if content:
                thumbnail_filename = f"{info['title']}_{unique_id}.jpg"
                thumbnail_filepath = os.path.join(thumbnail_dest, thumbnail_filename)
                with open(thumbnail_filepath, "wb") as f:
                    f.write(content)

        return DownloadResult({
            "platform": Platform.YOUTUBE,
            "title": info["title"],
            "files": [FileInfo(filename=filename, filepath=filepath)],
            "metadata": {
                "thumbnail_filename": thumbnail_filename,
                "thumbnail_filepath": thumbnail_filepath
            }
        })