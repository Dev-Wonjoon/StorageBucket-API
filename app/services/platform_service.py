from typing import List
from app.models.platform import Platform
from app.models.media import Media
from fastapi import HTTPException
from sqlmodel.ext.asyncio.session import AsyncSession 
from sqlmodel import select


class PlatformService:
    
    @classmethod
    async def add_platform(cls, name: str, session: AsyncSession) -> Platform:
        existing = await session.scalar(select(Platform).where(Platform.name == name))
        if existing:
            raise HTTPException(status_code=409, detail=f"이미 존재하는 플랫폼입니다.: {name}")
        
        platform = Platform(name=name)
        session.add(platform)
        await session.commit()
        await session.refresh(platform)
        return platform
    
    @classmethod
    async def get_platform_by_name(cls, name: str, session: AsyncSession) -> Platform:
        platform = await session.scalar(
            select(Platform).where(Platform.name == name)
        )
        if not platform:
            raise HTTPException(status_code=404, detail=f"플랫폼을 찾을 수 없습니다: {name}")

        return platform
    
    async def get_or_create(self, name: str, session: AsyncSession) -> Platform:
        try:
            return await self.__class__.get_platform_by_name(name, session)
        except HTTPException as e:
            if e.status_code == 404:
                return await self.add_platform(name, session)
            raise
    
    @classmethod
    async def list_platform(cls, session: AsyncSession) -> List[Platform]:
        result = await session.exec(select(Platform))
        return result.all()
    
    @classmethod
    async def delete_platform(cls, name: str, session: AsyncSession) -> None:
        platform = await cls.get_platform_by_name(name, session)
        await session.delete(platform)
        await session.commit()