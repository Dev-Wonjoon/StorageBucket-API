from typing import List
from fastapi import HTTPException
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from core.models import Media, Tag, MediaTag


class TagService:

    async def add_tags():
        pass