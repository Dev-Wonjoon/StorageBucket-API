import re
from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from urllib.parse import urlparse
from pydantic import BaseModel
import uuid

from core.database import get_session
from core.tasks import schedule_download
from app.models.urls import Url
from app.services.instagram_services import InstagramService
from app.services.youtube_services import YoutubeService

router = APIRouter(prefix="/api/download", tags=["download"])

URL_SERVICE_MAP = {
    r"(?:^|\.)instagram\.com$": InstagramService,
    r"(?:^|\.)youtube\.com$": YoutubeService
}

class DownloadRequest(BaseModel):
    url: str

@router.post("", status_code=202)
async def download_url(
    request: DownloadRequest,
    background_tasks: BackgroundTasks,
    session: AsyncSession = Depends(get_session)
):
    parsed = urlparse(request.url)
    host = parsed.netloc.lower()
    
    for pattern, service_cls in URL_SERVICE_MAP.items():
        if re.search(pattern, host):
            exists = await session.scalar(select(Url).where(Url.url == request.url))
            if exists:
                raise HTTPException(
                    status_code=409,
                    detail=f"이미 다운로드된 URL입니다: {request.url}"
                )
            
            schedule_download(request.url, background_tasks, service_cls)
            
            return {"message": "다운로드 예약되었습니다.", "id": str(uuid.uuid4())}
    raise HTTPException(
        status_code=400,
        detail=f"지원하지 않는 플랫폼입니다: {host}"
    )