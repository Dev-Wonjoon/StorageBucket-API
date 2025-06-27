from typing import List, Optional
from fastapi import APIRouter, Query

from app.services.search_service import SearchService

router = APIRouter(prefix="/api/search", tags=["search"])

@router.get("", response_model=List[dict])
async def search_endpoint(
    q: Optional[str] = Query(None, min_length=1),
    owner_id: Optional[int] = Query(None),
    owner_name: Optional[str] = Query(None),
    platform: Optional[str] = Query(None),
    limit: int = Query(30, gt=0, le=100),
    offset: int = Query(0, ge=0),
):
    return await SearchService.search(q, owner_id, owner_name, platform, limit, offset)