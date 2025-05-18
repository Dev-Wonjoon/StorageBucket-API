import re
from typing import List, Optional
from sqlmodel.ext.asyncio.session import AsyncSession
from fastapi import APIRouter, HTTPException, Body, Depends, Query
from urllib.parse import urlparse
from .db import get_session
from .models import Media, Platform

from .service.media_service import MediaService
from .service.platform_service import PlatformService

from instagram.services import InstagramService
from youtube.services import YoutubeService

router = APIRouter(prefix="/api", tags=["download"])

URL_SERVICE_MAP = {
    r"(?:^|\.)instagram\.com$": InstagramService,
    r"(?:^|\.)youtube\.com$": YoutubeService
}

@router.post("/download")
async def download_url(
    url: str = Body(..., embed=True),
    session: AsyncSession = Depends(get_session)
):
    parsed = urlparse(url)
    host = parsed.netloc.lower()
    
    for pattern, ServiceClass in URL_SERVICE_MAP.items():
        if re.search(pattern, host):
            service = ServiceClass()
            return await service.download_and_save(url, session)
    
    raise HTTPException(
        status_code=400,
        detail=f"지원하지 않는 플랫폼입니다: {host}"
    )

@router.get("/media/list",response_model=List[Media],summary="Get paged media list")
async def get_media(
    cursor: Optional[int] = Query(None),
    limit: int = Query(30, ge=1, le=100),
    session: AsyncSession = Depends(get_session)
):
    return await MediaService.get_medialist_by_cursor(cursor, limit, session)


@router.get("/platform/list", response_model=List[Platform])
async def get_platform_list(session: AsyncSession = Depends(get_session)):
    return await PlatformService.list_platform(session)


@router.get("/platform/{platform_name}", response_model=List[Media])
async def get_platform_name_list(platform_name: str, session: AsyncSession = Depends(get_session)):
    return await MediaService.get_media_by_platform_name(platform_name, session)


