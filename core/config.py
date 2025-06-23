from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Literal, List, ClassVar
from sqlalchemy.engine import URL
from urllib.parse import quote_plus
import os


BASE_DIR: Path = Path(__file__).resolve().parent.parent

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file = ".env", env_file_encoding="utf-8", extra="ignore")

    # 데이터베이스 설정
    database_type: Literal["sqlite", "postgresql"] = "sqlite"
    
    # SQLite 설정
    sqlite_database_name: str = Field(alias="DB_NAME")
    
    # PostgreSQL 설정
    postgresql_database_name: str = Field(alias="DB_NAME")
    postgresql_user: str = Field(alias="DB_USERNAME")
    postgresql_password: str = Field(alias="DB_PASSWORD")
    postgresql_host: str = Field(alias="DB_HOST")
    postgresql_port: int = Field(alias="DB_PORT")

    # 작업 디렉토리
    work_directory: str = "downloads"

    @property
    def database_url(self) -> str:
        if self.database_type == "sqlite":
            return f"sqlite+aiosqlite:///{self.sqlite_database_name}.db"
        
        url_obj = URL.create(
            "postgresql+asyncpg",
            username=self.postgresql_user,
            password=self.postgresql_password,
            host=self.postgresql_host,
            port=self.postgresql_port,
            database=self.postgresql_database_name
        )
        
        return (url_obj.render_as_string(hide_password=False))
        
    DOMAIN_PATHS: List = {
        os.getenv("YT_DIR"),
        os.getenv("IG_DIR"),
    }
    
    base_dir: ClassVar[Path] = BASE_DIR


def configure_cors(app: FastAPI) -> None:
    app.add_middleware(
        CORSMiddleware,
        allow_origin_regex=r"^http://192\.168\.\d{1,3}\.\d{1,3}(:\d+)?$",
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )