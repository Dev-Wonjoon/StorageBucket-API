from typing import List
from fastapi import APIRouter, Depends, Query
from sqlmodel.ext.asyncio.session import AsyncSession
from core.database import get_session
from app.services.instagram_service import InstagramService
from app.models.profile import Profile


router = APIRouter(prefix="/api/instagram", tags=["Instagram"])

@router.get("/profile/{owner_id}", response_model=Profile)
async def read_profile(
    owner_id: int,
    session: AsyncSession = Depends(get_session)
):
    return await InstagramService.get_profile(owner_id, session)

@router.get("/profile/list", response_model=List[Profile])
async def get_list_profile(
    page: int = Query(1, ge=1, description="페이지 번호"),
    size: int = Query(30, ge=1, le=100, description="페이지 크기"),
    session: AsyncSession = Depends(get_session)
):
    return await InstagramService.list_profile(session, page, size)
