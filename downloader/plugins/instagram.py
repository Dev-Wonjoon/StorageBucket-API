from instaloader import Instaloader, Post, Profile, exceptions, StoryItem
from pathlib import Path
from urllib.parse import urlparse
from typing import List

from downloader.interfaces import Downloader, DownloadResult
from downloader.models import FileInfo
from utils.app_utils import uuid_generator
from utils.image_utils import convert_to_webp

import re, asyncio


class InstagramDownloader(Downloader):
    PLATFORM = "instagram"
    
    _IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".bmp", ".tif", ".tiff", ".heic", ".heif"}
    
    def __init__(self, platform_dir: Path):
        self.platform_dir = platform_dir
        self.platform_dir.mkdir(parents=True, exist_ok=True)

    def _create_loader(self, target_dir: Path, prefix: str) -> Instaloader:
        uid = uuid_generator()
        loader = Instaloader(
            dirname_pattern=str(target_dir),
            filename_pattern=f"{prefix}_{{shortcode}}_{uid}"
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
            raise RuntimeError(f"Instaloader 오류: {e}") from e
        
        return result
    
    async def _convert_to_webp(self, paths: list[Path]) -> list[Path]:
        converted: list[Path] = []
        for p in paths:
            if p.suffix.lower() in self._IMAGE_EXTS:
                dst = p.with_suffix(".webp")
                await asyncio.to_thread(convert_to_webp, p, dst)
                p.unlink(missing_ok=True)
                converted.append(dst)
            else:
                converted.append(p)
        return converted
    
    def _download_post(self, url: str) -> DownloadResult:
        shortcode = url.split('/')[-1]
        base_loader = Instaloader()
        post = Post.from_shortcode(base_loader.context, shortcode)
        owner_id = post.owner_id
        dest = self._prepare_target(f"posts/{owner_id}")
        
        loader = self._create_loader(dest, post.owner_username)
        expect_paths = self._predict_post_files(loader, post, dest)
        
        loader.download_post(post, target="")
        
        saved_paths = [p for p in expect_paths if p.exists()]
        saved_paths = asyncio.run(self._convert_to_webp(saved_paths))
        files = [FileInfo(p.name, p) for p in saved_paths] or self._collect_files(dest)
        
        caption = post.caption or "caption_empty"
        metadata = {
            "caption": caption,
            "owner_id": owner_id,
            "owner_username": post.owner_username
        }
        
        return DownloadResult(
            platform=self.PLATFORM,
            title=caption,
            files=files,
            metadata=metadata
        )
    
    def _download_profile(self, url: str) -> DownloadResult:
        username = url.strip('/').split('/')[0]
        base_loader = Instaloader()
        profile = Profile.from_username(base_loader.context, username)
        owner_id = profile.userid
        
        dest = self._prepare_target(f"posts/{owner_id}")
        loader = self._create_loader(dest, username)
        loader.download_profile(profile, profile_pic_only=False, fast_update=True)
        
        files = self._collect_files(dest)
        files = asyncio.run(self._convert_to_webp([f.filepath for f in files]))
        files = [FileInfo(p.name, p) for p in files]
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
                    except_paths = self._predict_story_files(loader, item, dest)
                    loader.download_storyitem(item, target="")
                    saved_files = [p for p in except_paths if p.exists()]
                    saved_files = asyncio.run(self._convert_to_webp(saved_files))
                    files = [FileInfo(p.name, p) for p in saved_files] or self._collect_files(dest)
                    break
            if files:
                break

        if not files:
            raise ValueError(f"Story {story_id} not found for user {owner_name}")
        metadata = {"owner_id": owner_id, "owner_name": owner_name}
        return DownloadResult(
            platform=self.PLATFORM,
            title=owner_name,
            files=files,
            metadata=metadata
        )
    
    def _predict_post_files(
        self, loader: Instaloader, post: Post, dest: Path
    ) -> List[Path]:
        paths: List[Path] = []
        
        if post.typename == "GraghSidecar":
            for node in post.get_sidecar_nodes():
                stem = loader.format_filename(node, target="")
                ext = ".mp4" if node.is_video else ".webp"
                paths.append(dest / f"{stem}{ext}")
        else:
            stem = loader.format_filename(post, target="")
            ext = ".mp4" if post.is_video else ".webp"
            paths.append(dest / f"{stem}{ext}")
            
        return paths
    
    def _predict_story_files(
        self, loader: Instaloader, item: StoryItem, dest: Path
    ) -> List[Path]:
        stem = loader.format_filename(item, target="")
        ext = ".mp4" if item.is_video else ".webp"
        return [dest / f"{stem}{ext}"]
    
    def _prepare_target(self, subdir: str) -> Path:
        dest = self.platform_dir / subdir
        dest.mkdir(parents=True, exist_ok=True)
        return dest