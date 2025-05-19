from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlmodel.ext.asyncio.session import AsyncSession

from core.models import Media
from core.service.media_service import MediaService
from core.database import get_session

router = APIRouter(prefix="/api/media", tags=["media"])


@router.get("/list", response_model=List[Media], summary="Get paged media list")
async def get_media(
    cursor: Optional[int] = Query(None),
    limit: int = Query(30, ge=1, le=100),
    session: AsyncSession = Depends(get_session)
):
    """
    페이지네이션된 미디어 목록을 조회합니다.
    """
    return await MediaService.get_medialist_by_cursor(cursor, limit, session)


@router.get("/platform/{platform_name}", response_model=List[Media])
async def get_media_by_platform(
    platform_name: str, 
    session: AsyncSession = Depends(get_session)
):
    """
    특정 플랫폼의 미디어 목록을 조회합니다.
    """
    return await MediaService.get_media_by_platform_name(platform_name, session) 