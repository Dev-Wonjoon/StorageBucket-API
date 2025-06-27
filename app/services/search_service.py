from typing import List, Optional, Any, Dict
from core.meili import search_media


class SearchService:
    @staticmethod
    async def search(
        q: Optional[str],
        owner_id: Optional[int],
        owner_name: Optional[str],
        platform: Optional[str],
        limit: int,
        offset: int
    ) -> List[Dict[str, Any]]:
        filters = []
        if owner_id is not None:
            filters.append(f"owner_id = {owner_id}")
        if owner_name:
            filters.append(f"owner_name = '{owner_name}'")
        if platform:
            filters.append(f"platform = '{platform}'")
        filter_str = " AND ".join(filters) if filters else ""
        
        res = await search_media(
            query=q or "",
            filters=filter_str,
            limit=limit,
            offset=offset
        )
        hits = getattr(res, 'hits', [])
        return hits