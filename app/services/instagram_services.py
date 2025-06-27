from typing import List
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from fastapi import HTTPException

from app.models.profile import Profile
from app.models.media import Media
from app.models.urls import Url
from app.services.platform_service import PlatformService
from downloader.ig_downloader import InstagramDownloader
from downloader.base import DownloadResult
from utils.app_utils import now_kst

class InstagramService:
    def __init__(self):
        self.downloader = InstagramDownloader()
        self.platform_service = PlatformService()

    async def download_and_save(
        self, url: str, session: AsyncSession
    ) -> DownloadResult:
        
        existing = await session.scalar(select(Url).where(Url.url == url))
        if existing:
            raise HTTPException(
                status_code=409,
                detail="이미 존재하는 URL입니다."
            )

        try:
            result = await self.downloader.download(url)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Instagram 다운로드 실패: {e}")
        
        metadata = result.metadata or {}
        owner_id = metadata.get("owner_id")
        owner_name = metadata.get("owner_name")
        caption = (metadata.get("caption") or "").strip() or None

        if owner_id is None:
            raise HTTPException(status_code=500, detail="owner id 정보가 없습니다.")
        
        profile = await session.get(Profile, owner_id)
        if not profile:
            profile = Profile(
                owner_id=owner_id,
                owner_name=owner_name
            )
            session.add(profile)
        elif owner_name and profile.owner_name != owner_name:
            profile.owner_name = owner_name
            session.add(profile)

        platform = await self.platform_service.get_or_create(result.platform, session)
        
        url_obj = Url(url=url)
        session.add(url_obj)
        await session.commit()
        await session.refresh(url_obj)

        media_obj = []
        for file in result.files:
            title = caption or file.filename
            media = Media(
                platform_id=platform.id,
                filepath=str(file.filepath),
                filename=file.filename,
                title=title,
                owner_id=owner_id,
                owner_name=owner_name,
                url_id=url_obj.id,
                created_at=now_kst()
            )
            session.add(media)
            media_obj.append(media)
        await session.commit()
        for media in media_obj:
            await session.refresh(media)
        return result
    

    async def get_profile(owner_id: int, session: AsyncSession):
        profile = await session.get(Profile, owner_id)
        if profile is None:
            raise HTTPException(404, "해당 owner id의 프로필이 존재하지 않습니다.")
        return profile

    async def list_profile(
            session: AsyncSession,
            page: int,
            size: int
    ) -> List[Profile]:
        stmt = (
            select(Profile).order_by(Profile.owner_id)
            .offset((page - 1) * size).limit(size)
        )
        return (await session.exec(stmt)).all()