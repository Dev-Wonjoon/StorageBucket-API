import asyncio, httpx, yt_dlp
from pathlib import Path
from typing import Any, Dict, Optional

from downloader.models import FileInfo, DownloadResult, ExtractionResult
from downloader.interfaces import Downloader, Extractor
from utils.app_utils import safe_string, uuid_generator
from utils.image_utils import convert_to_webp
from utils.ytdlp_utils import YtOptsBuilder, VideoContainer


def _ensure_dir(p: Path) -> Path:
    p.mkdir(parents=True, exist_ok=True)
    return p


class GenericDownloader(Downloader[Dict[str, Any]]):
    def __init__(
        self,
        *,
        platform: str,
        root_dir: Path,
        extractor: Optional[Extractor[Dict[str, Any]]] = None,
        http_client: Optional[httpx.AsyncClient] = None,
    ):
        self.platform = platform.lower()
        self.extractor = extractor or GenericExtractor(self.platform)
        self.http = http_client or httpx.AsyncClient(timeout=10)
        
        self.platform_dir = _ensure_dir(root_dir.expanduser()/ "downloads" / self.platform)
        self.thumbnail_dir = _ensure_dir(self.platform_dir / "thumbnails")
        
    async def download(self, url: str) -> DownloadResult:
        meta = await self.extractor.extract(url)
        
        uid = uuid_generator()
        video_info = await self._download_video(meta, uid)
        thumbnail_info = await self._handle_thumbnail(meta.thumbnail_url, meta.title, uid)
        
        files = [video_info]
        if thumbnail_info:
            files.append(FileInfo(filename=thumbnail_info.filename, filepath=thumbnail_info.filepath))
        
        return DownloadResult(
            title=meta.title,
            platform=self.platform,
            files=files,
            metadata=meta.metadata,
        )
    
    def _build_filename(self, title: str, uid: str, ext: str) -> str:
        return f"{safe_string(title)}_{uid}.{ext}"

    async def _download_video(
        self, meta: ExtractionResult, uid: str, container: VideoContainer = VideoContainer.mp4
    ) -> FileInfo:
        dest_stem = self.platform_dir / f"{safe_string(meta.title)}_{uid}"
        ydl_opts = (
            YtOptsBuilder()
            .best_video_audio()
            .merge_output(container)
            .outtmpl(f"{dest_stem}.%(ext)s")
            .build()
        )

        def _run():
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([meta.video_url])

        await asyncio.to_thread(_run)
        fp = dest_stem.with_suffix(f".{meta.ext}")
        return FileInfo(filename=fp.name, filepath=fp)

    async def _handle_thumbnail(
        self, url: Optional[str], title: str, uid: str
    ) -> Optional[FileInfo]:
        if not url:
            return None, None
        data = await self._fetch(url)
        if not data:
            return None, None

        webp = await asyncio.to_thread(convert_to_webp, data)
        filename = self._build_filename(title, uid, "webp")
        filepath = self.thumbnail_dir / filename
        filepath.write_bytes(webp)
        return FileInfo(filename=filename, filepath=filepath)

    async def _fetch(self, url: str) -> Optional[bytes]:
        resp = await self.http.get(url)
        return resp.content if resp.status_code == 200 else None


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