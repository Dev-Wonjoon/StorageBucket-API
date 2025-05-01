from .base import Downloader, DownloadResult, FileInfo, Platform
from urllib.parse import urlparse
from instaloader import Instaloader, Post, Profile
from typing import List
from uuid import uuid4
import re
import os
import asyncio

DOWNLOAD_DIR = os.getenv("DOWNLOAD_DIR", "downloaders")

class InstagramDownloader(Downloader):

    def _create_loader(self, dest: str, filename_prefix: str) -> Instaloader:
        loader = Instaloader()
        loader.dirname_pattern = dest
        loader.filename_pattern = f"{filename_prefix}_{uuid4().hex[:8]}"
        loader.save_metadata = False
        return loader
    
    async def download(self, url: str) -> DownloadResult:
        parsed = urlparse(url)
        path = parsed.path

        if re.search(r"/(p|reel)/", path):
            return await asyncio.to_thread(self._download_shortcode, path)
        if re.match(r"^/stories/[^/]+/[^/]+/?$", path):
            return await asyncio.to_thread(self._download_stories, path)
        
        return await asyncio.to_thread(self.download_profile, path)
        
    def _download_shortcode(self, url: str) -> DownloadResult:
        shortcode = url.rstrip("/").split("/")[-1]
        base_loader = Instaloader()
        post = Post.from_shortcode(base_loader.context, shortcode)
        dest = os.path.join(DOWNLOAD_DIR, "instagram", str(post.owner_id))
        os.makedirs(dest, exist_ok=True)

        before = set(os.listdir(dest))

        loader = self._create_loader(dest, post.owner_username)
        post = Post.from_shortcode(loader.context, shortcode)
        loader.download_post(post, target="")

        after = set(os.listdir(dest))
        new_files = sorted(after - before)

        file_infos: List[FileInfo] = [
            FileInfo(filepath=os.path.join(dest, fname), filename=fname)
            for fname in new_files
        ]


        return DownloadResult({
            "platform": Platform.INSTAGRAM,
            "files": file_infos,
            "metadata": {
                "caption": post.caption,
                "owner_id": post.owner_id,
                "owner_name": post.owner_username
            }
        })
    
    def download_profile(self, loader: Instaloader, url: str) -> DownloadResult:
        username = urlparse(url).path.strip("/").split("/")[0]
        profile = Profile.from_username(loader.context, username)
        owner_id = profile.userid
        download_dir = os.path.join(DOWNLOAD_DIR, "instagram")
        dest = os.path.join(download_dir, str(owner_id))
        os.makedirs(exist_ok=True)

        loader.dirname_pattern = dest
        loader.download_profile(
            profile,
            profile_pic_only=False,
            fast_update=True,
        )

        file_infos = [
            {"filepath": os.path.join(dest, f), "filename": f}
            for f in os.listdir(dest)
        ]

        return {
            "platform": Platform.INSTAGRAM,
            "files": file_infos,
            "metadata": {
                "owner_id": profile.userid,
                "owner_name": profile.username
            }
        }
    

    def _download_stories(self, loader: Instaloader, url: str) -> DownloadResult:
        _, _, owner_name, story_id, *_ = urlparse(url).path.strip("/").split("/")
        profile = Profile.from_username(loader.context, username=owner_name)
        owner_id = profile.userid

        dest = os.path.join(DOWNLOAD_DIR, "instagram", str(owner_id))
        os.makedirs(dest, exist_ok=True)

        file_infos: list[FileInfo] = []
        
        for story in loader.get_stories(userids=[owner_id]):
            for item in story.get_items():
                if str(item.mediaid) != story_id:
                    continue

                loader.download_storyitem(item, target=dest)

                for fname in os.listdir(dest):
                    if story_id not in fname:
                        continue
                    old_path = os.path.join(dest, fname)
                    ext = os.path.splitext(fname)[1]
                    short_id = uuid4().hex[:8]
                    new_filename = f"{owner_name}_{short_id}{ext}"
                    new_path = os.path.join(dest, new_filename)
                    os.rename(old_path, new_path)
                    file_infos.append({
                        "filepath": new_path,
                        "filename": new_filename
                    })
                break
            else:
                continue
            break

        if not file_infos:
            raise ValueError(f"Story {story_id} not found for user {owner_name}")
        
        return {
            "platform": Platform.INSTAGRAM,
            "files": file_infos,
            "metadata": {
                "owner_id": owner_id,
                "owner_name": owner_name,

            }
        }