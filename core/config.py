from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Literal, List
import os



class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file = ".env", env_file_encoding="utf-8", extra="ignore")

    database_type: Literal["sqlite", "postgresql"] = "sqlite"
    database_name: str = "bucket.db"

    database_user: str | None = None
    database_password: str | None = None
    database_host: str = "localhost"
    database_port: int = 5432

    work_directory: str = os.getenv("DOWNLOAD_DIR")

    @property
    def database_url(self) -> str:
        if self.database_type == "sqlite":
            return f"sqlite+aiosqlite:///{self.database_name}"
        elif self.database_type == "postgresql":
            return (
                f"postgresql+asyncpg://{self.database_user}:{self.database_password}"
                f"@{self.database_host}:{self.database_port}/{self.database_name}"
            )
        
    DOMAIN_PATHS: List = {
        os.getenv("YT_DIR"),
        os.getenv("IG_DIR"),
    }


def configure_cors(app: FastAPI) -> None:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:5173"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )