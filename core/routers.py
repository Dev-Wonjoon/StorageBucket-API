import re
from typing import List
from instagram.services import InstagamService
from youtube.services import YoutubeService
from sqlmodel.ext.asyncio.session import AsyncSession
from fastapi import APIRouter, Depends, HTTPException, Body
from urllib.parse import urlparse
from .db import get_session
from .models import Media
from .media_service import MediaService

router = APIRouter(prefix="/api", tags=["download"])

URL_SERVICE_MAP = {
    r"(?:^|\.)instagram\.com$": InstagamService,
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

@router.get("/media", response_model=List[Media])
async def get_media_list(session: AsyncSession = Depends(get_session)):
    return await MediaService.list_media(session)