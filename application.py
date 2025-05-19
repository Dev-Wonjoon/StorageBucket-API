from fastapi import FastAPI
from contextlib import asynccontextmanager
from core.routers import router as core_router
from instagram.routers import router as insta_router
from core.routers.tag_router import router as tag_router
from core.config import configure_cors
from core.database import init_db

@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield


app = FastAPI(title="StorageBucket", lifespan=lifespan)
configure_cors(app)
app.include_router(core_router)
app.include_router(insta_router)
app.include_router(tag_router)

@app.get("/health")
async def healthcheck():
    return {"status": "ok"}
