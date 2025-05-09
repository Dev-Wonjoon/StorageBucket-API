from typing import List
from fastapi import APIRouter, Depends, Query
from sqlmodel.ext.asyncio.session import AsyncSession
from core.db import get_session
from .services import InstagramService
from .schemas import ProfileSchema
from .models import Profile


router = APIRouter(prefix="/api/instagram", tags=["Instagram"])

@router.get("/profile/{owner_id}", response_model=ProfileSchema)
async def read_profile(
    owner_id: int,
    session: AsyncSession = Depends(get_session)
):
    return await InstagramService.get_profile(owner_id, session)

@router.get("/profile", response_model=List[Profile])
async def get_list_profile(
    page: int = Query(1, ge=1, description="페이지 번호"),
    size: int = Query(30, ge=1, le=100, description="페이지 크기"),
    session: AsyncSession = Depends(get_session)
):
    return await InstagramService.list_profile(session, page, size)