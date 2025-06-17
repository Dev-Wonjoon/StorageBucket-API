import asyncio
import os
import yt_dlp
import requests
import uuid
from PIL import Image
from io import BytesIO

from typing import Any, Dict, List
from downloader.base import Downloader, FileInfo, Platform, DownloadResult


DOWNLOAD_DIR = os.getenv("DOWNLOAD_DIR", "downloads")


class YoutubeDownloader(Downloader):

    async def thumbnail_download(self, url: str):
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        origin_bytes = response.content
        
        img = Image.open(BytesIO(origin_bytes)).convert("RGB")
        buf = BytesIO()
        img.save(buf, format="WEBP", quality=100, optimize=True, method=3)

        return buf.getvalue()


    async def download(self, url: str) -> DownloadResult:
        dest = os.path.join(DOWNLOAD_DIR, "youtube")
        thumbnail_dest = os.path.join(DOWNLOAD_DIR, "thumbnails")
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