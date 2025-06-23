from fastapi import FastAPI
from contextlib import asynccontextmanager
from fastapi.staticfiles import StaticFiles

from app.routers.download_router import router as download_router
from app.routers.media_router import router as media_router
from app.routers.platform_router import router as platform_router
from app.routers.tag_router import router as tag_router
from app.routers.routers import router as insta_router
from core.config import configure_cors
from core.database import init_db
from core.migrations import upgrade_to_head

import os

async def lifespan(app: FastAPI):
    import logging, time
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s")

    t0 = time.perf_counter()
    logging.info("★ step 1: init_db 시작")
    await init_db()
    logging.info("★ step 1: init_db 끝 (%.2fs)", time.perf_counter() - t0)

    t1 = time.perf_counter()
    logging.info("★ step 2: alembic upgrade 시작")
    await upgrade_to_head()
    logging.info("★ step 2: alembic upgrade 끝 (%.2fs)", time.perf_counter() - t1)

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
