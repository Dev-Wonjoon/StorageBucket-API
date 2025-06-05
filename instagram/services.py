from typing import List
from sqlmodel import select, func
from sqlmodel.ext.asyncio.session import AsyncSession
from fastapi import HTTPException
from sqlalchemy.orm import selectinload
from .models import Profile
from core.models import Media, Url
from media.services.platform_service import PlatformService
from downloader.instagram_downloader import InstagramDownloader
from downloader.base import DownloadResult, FileInfo

class InstagramService:
    def __init__(self):
        self.downloader = InstagramDownloader()
        self.platform_service = PlatformService()

    async def download_and_save(
        self, url: str, session: AsyncSession
    ) -> DownloadResult:
        
        url_obj = await session.scalar(select(Url).where(Url.url == url))
        if url_obj:
            raise HTTPException(
                status_code=409,
                detail="이미 존재하는 URL입니다."
            )

        try:
            result = await self.downloader.download(url)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Instagram 다운로드 실패: {e}")
        
        platform_name = result["platform"].value
        files: list[FileInfo] = result["files"]
        metadata = result.get("metadata", {})

        owner_id = metadata.get("owner_id")
        owner_name = metadata.get("owner_name")
        caption = metadata.get(("caption")or "").strip()

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

        platform = await self.platform_service.get_or_create(platform_name, session)
        
        is_new_url = False
        if url_obj is None:
            url_obj = Url(url=url)
            session.add(url_obj)
            await session.commit()
            await session.refresh(url_obj)
            is_new_url = True

        if is_new_url:
            for f_info in files:
                title = caption if caption else f_info["filename"]

                media = Media(
                    platform=platform,
                    filepath=f_info["filepath"],
                    filename=f_info["filename"],
                    title=title,
                    owner_id=owner_id,
                    owner_name=owner_name,
                    url_id=url_obj.id
                )
                session.add(media)
            await session.commit()
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