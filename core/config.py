from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
from pydantic import Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Literal, ClassVar, Optional
from sqlalchemy.engine import URL
import os

class _Default:
    DB_TYPE: Literal["sqlite", "postgresql"] = "sqlite"
    DEBUG: bool = True
    WEB_PORT: int = 8000
    
    SQLITE_DB_NAME = "storagebucket"
    
    PG_NAME = "storagebucket"
    PG_USER = "postgres"
    PG_PWD = "postgres"
    PG_HOST = "localhost"
    PG_PORT = 5432
    
    BASE_DIR = Path(__file__).resolve().parent.parent
    DOWNLOAD_DIR = BASE_DIR / "downloads"
    YT_VIDEO_DIR = "youtubes"
    YT_THUMBNAIL_DIR = "thumbnails"
    IG_DIR = "instagrams"
    LOCAL_DIR = "local"
    

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file = ".env", env_file_encoding="utf-8", extra="ignore")
    debug: bool = Field(default=_Default.DEBUG)
    database_type: str = Field(default=_Default.DB_TYPE, alias="DATABASE_TYPE")
    
    sqlite_database_name: str = Field(default=_Default.SQLITE_DB_NAME, alias="SQLITE_DB_NAME")
    
    postgres_database_name: str = Field(default=_Default.PG_NAME, alias="PG_NAME")
    postgres_user: str = Field(default=_Default.PG_USER, alias="PG_USERNAME")
    postgres_password: str = Field(default=_Default.PG_PWD, alias="PG_PASSWORD")
    postgres_host: str = Field(default=_Default.PG_HOST, alias="PG_HOST")
    postgres_port: int = Field(default=_Default.PG_PORT, alias="PG_PORT")
    
    meili_key: str = Field(alias="MEILI_MASTER_KEY")
    meili_url: str = Field(alias="MEILI_URL")
    
    base_dir: ClassVar[Path] = _Default.BASE_DIR
    download_dir: Path = Field(
        default_factory=lambda: Path(
            os.getenv("DOWNLOAD_DIR", _Default.DOWNLOAD_DIR)))
    yt_video_dir: Optional[Path] = None
    yt_thumbnail_dir: Optional[Path] = None
    ig_dir: Optional[Path] = None
    local_dir: Optional[Path] = None
    
    @model_validator(mode="after")
    def _populate_subdir(self):
        self.yt_video_dir = self.yt_video_dir or self.download_dir / _Default.YT_VIDEO_DIR
        self.yt_thumbnail_dir = self.yt_thumbnail_dir or self.download_dir / _Default.YT_THUMBNAIL_DIR
        self.ig_dir = self.ig_dir or self.download_dir / _Default.IG_DIR
        self.local_dir = self.local_dir or self.download_dir / _Default.LOCAL_DIR
        
        return self
    
    @property
    def database_url(self) -> str:
        if self.database_type == 'sqlite':
            return f"sqlite+aiosqlite:///{self.sqlite_database_name}.db"
        
        elif self.database_type == "postgresql":
        
            url_obj = URL.create(
                "postgresql+asyncpg",
                username=self.postgres_user,
                password=self.postgres_password,
                host=self.postgres_host,
                port=self.postgres_port,
                database=self.postgres_database_name
            )
            return (url_obj.render_as_string(hide_password=False))
        
        else:
            return f"sqlite+aiosqlite:///{self.sqlite_database_name}.db"


def configure_cors(app: FastAPI) -> None:
    app.add_middleware(
        CORSMiddleware,
        allow_origin_regex=r"^http://192\.168\.\d{1,3}\.\d{1,3}(:\d+)?$",
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )