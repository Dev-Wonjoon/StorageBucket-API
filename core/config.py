from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Literal, List, Union, Optional
import os


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file = ".env", env_file_encoding="utf-8", extra="ignore")

    # 데이터베이스 설정
    database_type: Literal["sqlite", "postgresql"] = "sqlite"
    
    # SQLite 설정
    sqlite_database_name: str = "bucket.db"
    
    # PostgreSQL 설정
    postgresql_database_name: str = "storagebucket"
    postgresql_user: str = "postgres"
    postgresql_password: str = "postgres"
    postgresql_host: str = "localhost"
    postgresql_port: int = 5432

    # 작업 디렉토리
    work_directory: str = "downloads"

    @property
    def database_url(self) -> str:
        if self.database_type == "sqlite":
            return f"sqlite+aiosqlite:///{self.sqlite_database_name}"
        elif self.database_type == "postgresql":
            return (
                f"postgresql+asyncpg://{self.postgresql_user}:{self.postgresql_password}"
                f"@{self.postgresql_host}:{self.postgresql_port}/{self.postgresql_database_name}"
            )
        
    DOMAIN_PATHS: List = {
        os.getenv("YT_DIR"),
        os.getenv("IG_DIR"),
    }


def configure_cors(app: FastAPI) -> None:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:5173", "http://192.168.1.172:5173"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )