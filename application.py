from fastapi import FastAPI
from contextlib import asynccontextmanager

from fastapi.staticfiles import StaticFiles
from media.routers.download_router import router as download_router
from media.routers.media_router import router as media_router
from media.routers.platform_router import router as platform_router
from media.routers.tag_router import router as tag_router
from instagram.routers import router as insta_router
from core.config import configure_cors
from core.database import init_db

import os

@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield


DOWNLOAD_DIR = os.getenv("DOWNLOAD_DIR", "downloads")
os.makedirs(DOWNLOAD_DIR, exist_ok=True)
app = FastAPI(debug=True, title="StorageBucket", lifespan=lifespan)

app.mount("/api/file", StaticFiles(directory=DOWNLOAD_DIR, html=False), name="downloads")

configure_cors(app)
app.include_router(download_router)
app.include_router(media_router)
app.include_router(platform_router)
app.include_router(tag_router)
app.include_router(insta_router)


@app.get("/health")
async def healthcheck():
    return {"status": "ok"}
