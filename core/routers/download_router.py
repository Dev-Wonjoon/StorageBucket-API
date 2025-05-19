import re
from fastapi import APIRouter, HTTPException, Body, Depends
from sqlmodel.ext.asyncio.session import AsyncSession
from urllib.parse import urlparse

from core.database import get_session
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