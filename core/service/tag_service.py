from typing import List
from fastapi import HTTPException
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from core.models import Media, Tag


class TagService:

    @classmethod
    async def add_tag(cls, name: str, session: AsyncSession) -> Tag:
        existing = await session.scalar(select(Tag).where(Tag.name == name))
        if existing:
            raise HTTPException(status_code=409, detail=f"이미 존재하는 태그입니다: {name}")
        
        tag = Tag(name=name)
        session.add(tag)
        await session.commit()
        await session.refresh(tag)
        return tag
    
    @classmethod
    async def get_tag_by_name(cls, name: str, session: AsyncSession) -> Tag:
        tag = await session.scalar(
            select(Tag).where(Tag.name == name)
        )
        if not tag:
            raise HTTPException(status_code=404, detail=f"태그를 찾을 수 없습니다: {name}")
        
        return tag
    
    @classmethod
    async def get_or_create(cls, name: str, session: AsyncSession) -> Tag:
        try:
            return await cls.get_tag_by_name(name, session)
        except HTTPException as e:
            if e.status_code == 404:
                return await cls.add_tag(name, session)
            raise
    
    @classmethod
    async def list_tags(cls, session: AsyncSession) -> List[Tag]:
        result = await session.exec(select(Tag))
        return result.all()
    
    @classmethod
    async def delete_tag(cls, name: str, session: AsyncSession) -> None:
        tag = await cls.get_tag_by_name(name, session)
        await session.delete(tag)
        await session.commit()
    
    @classmethod
    async def add_tags_to_media(cls, media_id: int, tag_names: List[str], session: AsyncSession) -> Media:
        media = await session.get(Media, media_id)
        if not media:
            raise HTTPException(status_code=404, detail=f"미디어를 찾을 수 없습니다: {media_id}")
        
        for tag_name in tag_names:
            tag = await cls.get_or_create(tag_name, session)
            if tag not in media.tags:
                media.tags.append(tag)
        
        await session.commit()
        await session.refresh(media)
        return media
    
    @classmethod
    async def remove_tags_from_media(cls, media_id: int, tag_names: List[str], session: AsyncSession) -> Media:
        media = await session.get(Media, media_id)
        if not media:
            raise HTTPException(status_code=404, detail=f"미디어를 찾을 수 없습니다: {media_id}")
        
        for tag_name in tag_names:
            try:
                tag = await cls.get_tag_by_name(tag_name, session)
                if tag in media.tags:
                    media.tags.remove(tag)
            except HTTPException:
                continue  # 태그가 없으면 무시
        
        await session.commit()
        await session.refresh(media)
        return media
    
    @classmethod
    async def get_media_by_tag(cls, tag_name: str, session: AsyncSession) -> List[Media]:
        tag = await cls.get_tag_by_name(tag_name, session)
        return tag.media
    
    @classmethod
    async def add_tags_to_multiple_media(
        cls, 
        media_ids: List[int], 
        tag_names: List[str], 
        session: AsyncSession
    ) -> List[Media]:
        """
        여러 미디어에 여러 태그를 추가합니다.
        
        Args:
            media_ids: 태그를 추가할 미디어 ID 목록
            tag_names: 추가할 태그 이름 목록
            session: 데이터베이스 세션
            
        Returns:
            업데이트된 미디어 객체 목록
        """
        # 모든 미디어 조회
        media_list = []
        for media_id in media_ids:
            media = await session.get(Media, media_id)
            if not media:
                raise HTTPException(
                    status_code=404, 
                    detail=f"미디어를 찾을 수 없습니다: {media_id}"
                )
            media_list.append(media)
        
        # 모든 태그 생성 또는 조회
        tags = []
        for tag_name in tag_names:
            tag = await cls.get_or_create(tag_name, session)
            tags.append(tag)
        
        # 각 미디어에 태그 추가
        updated_media = []
        for media in media_list:
            for tag in tags:
                if tag not in media.tags:
                    media.tags.append(tag)
            updated_media.append(media)
        
        await session.commit()
        
        # 모든 미디어 새로고침
        for media in updated_media:
            await session.refresh(media)
        
        return updated_media