from instaloader import Instaloader, Post, Profile
from pathlib import Path
from urllib.parse import urlparse
from typing import List, Optional, Callable
from uuid import uuid4

from core import settings
from .base import Downloader, DownloadResult, FileInfo
from utils.youtube_utils import YtOptsBuilder

import httpx

RegDomainFn = Callable[[str], str]

class InstagramDownloader(Downloader):
    
    def __init__(
        self,
        media_dir: Path,
        thumb_dir: Optional[Path],         
        reg_media: RegDomainFn,
        
    ) -> None:
        self.media_dir = Path(media_dir).expanduser()
        self.thumb_dir = Path(thumb_dir or (media_dir / 'thumbnails'))