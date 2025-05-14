import asyncio
import os
import yt_dlp
import requests
import uuid

from typing import Any, Dict, List
from downloader.base import Downloader, FileInfo, Platform, DownloadResult


DOWNLOAD_DIR = os.getenv("DOWNLOAD_DIR", "downloads")


class YoutubeDownloader(Downloader):

    async def thumbnail_download(self, url: str):
        response = requests.get(url)

        if response.status_code == 200:
            return response.content
        else:
            print("다운로드 실패")


    async def download(self, url: str) -> DownloadResult:
        dest = os.path.join(DOWNLOAD_DIR, "youtube")
        os.makedirs(dest, exist_ok=True)

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
            content = await self.thumbnail_download(url)
            if content:
                thumbnail_filename = f"{info['title']}_{unique_id}.jpg"
                thumbnail_filepath = os.path.join(dest, thumbnail_filename)
                with open(thumbnail_filepath, "wb") as f:
                    f.write(content)

        return DownloadResult({
            "platform": Platform.YOUTUBE,
            "files": [FileInfo(filename=filename, filepath=filepath)],
            "metadata": {
                "thumbnail_filepath": thumbnail_filename,
                "thumbnail_filename": thumbnail_filepath
            }
        })