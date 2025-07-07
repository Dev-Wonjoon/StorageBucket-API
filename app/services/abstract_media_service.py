from abc import ABC, abstractmethod
from fastapi import HTTPException
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from typing import Any, Dict, Optional

from app.repositories.media_repository import MediaRepository
from app.models.platform import Platform
from core.exception import DuplicateUrlError
from core.unit_of_work import unit_of_work
from downloader.models import DownloadResult, FileInfo


class AbstractMediaService(ABC):
    """
    1) URL 처리 → 2) 다운로드 실행 → 3) Media 저장
    의 공통 시나리오를 제공하는 템플릿 서비스.
    """
    PLATFORM_NAME: str # 구현체에서 지정
    
    def __init__(self, session: AsyncSession) -> None:
        if not getattr(self, "PLATFORM_NAME", None):
            raise AttributeError(f"{self.__class__.__name__}는 PLATFORM_NAME을 지정해야 합니다.")
        self.session = session
        self._platform_id: int | None = None
        
    
    async def handle(self, url: str, **kwargs):
        """
        외부에서 호출하는 단일 진입점
        """
        try:
            url_obj = await self._get_or_create_url(url)
        except DuplicateUrlError:
            raise HTTPException(status_code=409, detail="이미 등록된 URL입니다.")
        
        result: DownloadResult = await self._download(url)
        
        metadata: Dict[str, Any] = result.metadata or {}
        caption: Optional[str] = metadata.get("caption")
        owner_id: Optional[int] = metadata.get("owner_id")
        owner_name: Optional[str] = metadata.get("owner_name")
        
        async with unit_of_work(self.session) as tx:
            await tx.flush()
            
            repo = MediaRepository(tx)
            await repo.add_medias(
                files=result.files,
                platform_id= await self._get_platform_id(),
                url_id=url_obj.id,
                owner_id=owner_id,
                owner_name=owner_name,
                caption=caption,
            )
            
            return result
    
    @abstractmethod
    async def _get_or_create_url(self, url: str):
        raise NotImplementedError
    
    @abstractmethod
    async def _download(self, url: str) -> DownloadResult:
        raise NotImplementedError
    
    async def _get_platform_id(self) -> int:
        if self._platform_id is not None:
            return self._platform_id
        
        stmt = select(Platform.id).where(Platform.name == self.PLATFORM_NAME)
        platform: Platform | None = (await self.session.exec(stmt)).first()
        
        if platform is None:
            platform = Platform(name=self.PLATFORM_NAME)
            self.session.add(platform)
            await self.session.flush()
        
        self._platform_id = platform.id
        return platform.id
        
            
    
    