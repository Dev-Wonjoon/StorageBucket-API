from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel.ext.asyncio.session import AsyncSession

from core.database import get_session
from core.models import Platform
from media.services.platform_service import PlatformService

router = APIRouter(prefix="/api/platform", tags=["platform"])


@router.post("", response_model=Platform)
async def create_platform(
    name: str,
    session: AsyncSession = Depends(get_session)
):
    """
    새로운 플랫폼을 생성합니다.
    
    - name: 플랫폼 이름 (예: youtube, instagram)
    """
    return await PlatformService.add_platform(name, session)


@router.get("/list", response_model=List[Platform])
async def get_platform_list(session: AsyncSession = Depends(get_session)):
    """
    모든 플랫폼 목록을 조회합니다.
    """
    return await PlatformService.list_platform(session)


@router.get("/{name}", response_model=Platform)
async def get_platform(
    name: str,
    session: AsyncSession = Depends(get_session)
):
    """
    이름으로 플랫폼을 조회합니다.
    """
    return await PlatformService.get_platform_by_name(name, session)


@router.delete("/{name}")
async def delete_platform(
    name: str,
    session: AsyncSession = Depends(get_session)
):
    """
    플랫폼을 삭제합니다.
    """
    await PlatformService.delete_platform(name, session)
    return {"message": f"플랫폼 '{name}'가 삭제되었습니다."}