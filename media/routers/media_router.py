from typing import List, Optional
from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, UploadFile
from sqlmodel.ext.asyncio.session import AsyncSession


from core.database import get_session
from core.models import Media
from media.services.media_service import MediaService

router = APIRouter(prefix="/api/media", tags=["media"])


@router.post("/upload", response_model=List[Media])
async def upload_media(
    files: List[UploadFile] = File(..., description="업로드할 미디어 파일"),
    platform_name: str = Form(..., ),
    tag_names: List[str] = Form(..., ),
):
    try:
        created_media_list = await MediaService.add_media(
            files=files,
            platform_name=platform_name,
            tag_names=tag_names,
        )
        return created_media_list
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"미디어 업로드 중 오류 발생: {str(e)}")


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

@router.get("/{media_id}", response_model=Media)
async def get_media_by_id(
    media_id: int,
    session: AsyncSession = Depends(get_session)
):
    return await MediaService.get_media_by_id(media_id, session)