from contextlib import asynccontextmanager
from sqlmodel.ext.asyncio.session import AsyncSession


@asynccontextmanager
async def unit_of_work(session: AsyncSession):
    try:
        yield session
        await session.commit()
    except Exception:
        await session.rollback()
        raise