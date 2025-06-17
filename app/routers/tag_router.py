from typing import List
from fastapi import APIRouter, Depends, Body
from sqlmodel.ext.asyncio.session import AsyncSession

from core.database import get_session
from app.models.media import Media
from app.models.tag import Tag
from app.services.tag_service import TagService

router = APIRouter(prefix="/api/tag", tags=["tag"])


@router.post("", response_model=Tag)
async def create_tag(name: str, session: AsyncSession = Depends(get_session)):
    """
    새 태그를 생성합니다.
    """
    return await TagService.add_tag(name, session)


@router.get("", response_model=List[Tag])
async def list_tags(session: AsyncSession = Depends(get_session)):
    """
    모든 태그 목록을 조회합니다.
    """
    return await TagService.list_tags(session)


@router.get("/{name}", response_model=Tag)
async def get_tag(name: str, session: AsyncSession = Depends(get_session)):
    """
    이름으로 태그를 조회합니다.
    """
    return await TagService.get_tag_by_name(name, session)


@router.delete("/{name}")
async def delete_tag(name: str, session: AsyncSession = Depends(get_session)):
    """
    태그를 삭제합니다.
    """
    await TagService.delete_tag(name, session)
    return {"message": f"태그 '{name}'가 삭제되었습니다."}


@router.post("/media/{media_id}", response_model=Media)
async def add_tags_to_media(
    media_id: int, 
    tag_names: List[str], 
    session: AsyncSession = Depends(get_session)
):
    """
    미디어에 태그를 추가합니다.
    """
    return await TagService.add_tags_to_media(media_id, tag_names, session)


@router.delete("/media/{media_id}", response_model=Media)
async def remove_tags_from_media(
    media_id: int, 
    tag_names: List[str], 
    session: AsyncSession = Depends(get_session)
):
    """
    미디어에서 태그를 제거합니다.
    """
    return await TagService.remove_tags_from_media(media_id, tag_names, session)


@router.get("/media/{tag_name}", response_model=List[Media])
async def get_media_by_tag(
    tag_name: str, 
    session: AsyncSession = Depends(get_session)
):
    """
    특정 태그가 붙은 모든 미디어를 조회합니다.
    """
    return await TagService.get_media_by_tag(tag_name, session)


@router.post("/media/batch", response_model=List[Media])
async def add_tags_to_multiple_media(
    media_ids: List[int] = Body(..., embed=True),
    tag_names: List[str] = Body(..., embed=True),
    session: AsyncSession = Depends(get_session)
):
    """
    여러 미디어에 여러 태그를 한 번에 추가합니다.
    
    - media_ids: 태그를 추가할 미디어 ID 목록
    - tag_names: 추가할 태그 이름 목록
    """
    return await TagService.add_tags_to_multiple_media(media_ids, tag_names, session)