from instaloader import Instaloader, Post, Profile, exceptions
from pathlib import Path
from urllib.parse import urlparse
from typing import List

from .base import Downloader, DownloadResult, FileInfo
from utils.app_utils import uuid_generator

import re, asyncio


class InstagramDownloader(Downloader):
    PLATFORM = "instagram"
    
    def __init__(self, media_dir: Path):
        self.media_dir = media_dir
        self.media_dir.mkdir(parents=True, exist_ok=True)

    def _create_loader(self, target_dir: Path, prefix: str) -> Instaloader:
        loader = Instaloader(
            dirname_pattern=str(target_dir),
            filename_pattern=f"{prefix}_{{shortcode}}_{uuid_generator}"
        )
        loader.save_metadata = False
        loader.post_metadata_txt_pattern = ""
        loader.storyitem_metadata_txt_pattern = ""
        return loader
    
    def _collect_files(self, target_dir: Path) -> List[FileInfo]:
        return [
            FileInfo(filename=file.name, filepath=file)
            for file in sorted(target_dir.iterdir())
            if file.is_file()
        ]
        
    def _prepare_target(self, subdir: str) -> Path:
        dest = self.media_dir / subdir
        
    async def download(self, url: str) -> DownloadResult:
        parsed = urlparse(url)
        path = parsed.path.rstrip("/")
        
        try:
            if re.match(r"^/(?:p|reel)/", path):
                result = await asyncio.to_thread(self._download_post, path)
            elif re.match(r"^/stories/[\w\.]+/[0-9]+$", path):
                result = await asyncio.to_thread(self._download_story, path)
            else:
                result = await asyncio.to_thread(self._download_profile, path)
        except exceptions.InstaloaderException as e:
            raise RuntimeError(f"Instaloader 오류: {e}")
        
        return result
    
    def _download_post(self, url: str) -> DownloadResult:
        shortcode = url.split('/')[-1]
        base_loader = Instaloader()
        post = Post.from_shortcode(base_loader.context, shortcode)
        owner_id = post.owner_id
        dest = self._prepare_target(f"posts/{owner_id}")
        
        loader = self._create_loader(dest, post.owner_username)
        loader.download_post(post, target="")
        
        files = self._collect_files(dest)
        caption = post.caption or 'caption_empty'
        metadata = {
            'caption': caption,
            'owner_id': post.owner_id,
            'owner_username': post.owner_username
        }
        return DownloadResult(platform=self.PLATFORM, title=caption, files=files, metadata=metadata)
    
    def _download_profile(self, url: str) -> DownloadResult:
        username = url.strip('/').split('/')[0]
        base_loader = Instaloader()
        profile = Profile.from_username(base_loader.context, username)
        owner_id = profile.userid
        
        dest = self._prepare_target(f"posts/{owner_id}")
        loader = self._create_loader(dest, username)
        loader.download_profile(profile, profile_pic_only=False, fast_update=True)
        
        files = self._collect_files(dest)
        metadata = {
            'owner_id': owner_id,
            'owner_name': profile.username
        }
        return DownloadResult(platform=self.PLATFORM, title=profile.username, files=files, metadata=metadata)
    
    def _download_story(self, url: str) -> DownloadResult:
        parts = url.strip('/').split('/')
        _, owner_name, story_id = parts[-3:]
        base_loader = Instaloader()
        profile = Profile.from_username(base_loader.context, owner_name)
        owner_id = profile.userid

        dest = self._prepare_target(f'stories/{owner_id}')
        loader = self._create_loader(dest, owner_name)

        files: List[FileInfo] = []
        for story in loader.get_stories(userids=[owner_id]):
            for item in story.get_items():
                if str(item.mediaid) == story_id:
                    loader.download_storyitem(item, target="")
                    files = self._collect_files(dest)
                    break
            if files:
                break

        if not files:
            raise ValueError(f"Story {story_id} not found for user {owner_name}")

        metadata = {'owner_id': owner_id, 'owner_name': owner_name}
        return DownloadResult(platform=self.PLATFORM, title=owner_name, files=files, metadata=metadata)
    