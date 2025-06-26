import os, uuid, aiofiles
from pathlib import Path
from typing import List, Optional, Sequence
from fastapi import HTTPException, UploadFile
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from app.models.media import Media
from app.services.tag_service import TagService
from app.services.platform_service import PlatformService
from core import settings

UPLOAD_DIR: Path = Path(settings.local_dir)
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

class MediaService:
    async def list_media(session: AsyncSession) -> List[Media]:
        stmt = select(Media)
        result = await session.exec(stmt)
        return result.all()
    
    async def get_medialist_by_cursor(
            cursor: Optional[int],
            limit: int,
            session: AsyncSession
    ) -> List[Media]:
        """
        cursor: 마지막으로 받은 Media.id (없으면 처음부터)
        limit: 한 번에 가져올 개수
        """
        stmt = select(Media).order_by(Media.id)
        if cursor is not None:
            stmt = stmt.where(Media.id > cursor)
        stmt = stmt.limit(limit)

        result = await session.exec(stmt)
        return result.all()
    
    async def get_media_by_platform_name(name: str, session: AsyncSession) -> list[Media]:
        platform = await PlatformService.get_platform_by_name(name=name, session=session)

        result = await session.exec(
            select(Media).where(Media.platform_id == platform.id)
        )

        return result.all()
    
    async def get_media_by_id(media_id: int, session: AsyncSession) -> Media:
        stmt = select(Media).where(Media.id == media_id)
        result = await session.exec(stmt)
        media = result.first()
        if not media:
            raise HTTPException(status_code=404, detail="Media not found")
        return media

    
    @classmethod
    async def add_media(
        cls,
        files: List[UploadFile],
        platform_name: str,
        tag_names: List[str],
        session: AsyncSession
    ) -> List[Media]:
        """
        미디어를 추가합니다.
        """
        platform_service = PlatformService()
        
        platform = await platform_service.get_or_create(platform_name, session)
        
        tags = [await TagService.get_or_create(name, session) for name in tag_names]
        
        created_media_list = []
        for file in files:
            unique_filename = f"{file.filename}_{uuid.uuid4().hex[:8]}"
            filepath = os.path.join(UPLOAD_DIR, unique_filename)
            
            with open(filepath, "wb") as buffer:
                content = await file.read()
                buffer.write(content)
                
            file_size = os.path.getsize(filepath)
            
            media = Media(
                title=file.filename,
                filepath=filepath,
                platform_id=platform.id,
                platform=platform,
                tags=tags,
                file_size=file_size
            )
            session.add(media)
            created_media_list.append(media)
        
        await session.commit()
        for media in created_media_list:
            await session.refresh(media)
        
        return created_media_list