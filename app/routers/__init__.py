from .download_router import router as download_routers
from .media_router import router as media_routers
from .insta_router import router as insta_routers
from .platform_router import router as platform_routers
from .tag_router import router as tag_routers
from .search_router import router as search_routers


ALL_ROUTERS = (
    download_routers,
    media_routers,
    platform_routers,
    tag_routers,
    insta_routers,
    search_routers
)