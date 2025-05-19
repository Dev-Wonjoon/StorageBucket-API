from fastapi import APIRouter
from core.routers.media_router import router as media_router
from core.routers.platform_router import router as platform_router
from core.routers.tag_router import router as tag_router
from core.routers.download_router import router as download_router

# 모든 라우터를 여기에 등록
router = APIRouter()

# 각 기능별 라우터 등록
router.include_router(media_router)
router.include_router(platform_router)
router.include_router(tag_router)
router.include_router(download_router) 