from fastapi import BackgroundTasks
from core.database import AsyncSessionLocal


def schedule_download(
    url: str,
    background_tasks: BackgroundTasks,
    service_cls: type,
) -> None:
    """
    URL 다운로드를 백그라운드 작업으로 예약합니다.
    """
    
    def _job():
        import asyncio
        async def _run():
            async with AsyncSessionLocal() as session:
                service = service_cls(session)
                await service.handle(url)
        
        asyncio.run(_run())
    background_tasks.add_task(_job)