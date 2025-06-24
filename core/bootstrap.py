from contextlib import asynccontextmanager
from fastapi.staticfiles import StaticFiles
from fastapi import FastAPI
from pathlib import Path

from app.routers import ALL_ROUTERS
from core import settings
from core.database import init_db

_static_method = False
_routers_registed = False


@asynccontextmanager
async def bootstrap(app: FastAPI):
    global _static_method, _routers_registed
    
    await init_db()
    
    if not _static_method:
        download_dir = Path(settings.download_dir)
        download_dir.mkdir(parents=True, exist_ok=True)
        
        app.mount("/app/file", StaticFiles(directory=str(download_dir), html=False))
        _static_method = True
        
    if not _routers_registed:
        for rt in ALL_ROUTERS:
            app.include_router(rt)
        _routers_registed = True
    
    yield
