from meilisearch_python_async import Client
from typing import Any, Dict, List, Union

from core.config import Settings

settings = Settings()

client = Client(settings.meili_url, settings.meili_key)

MEDIA_INDEX_NAME = "media"
MEDIA_PRIMARY_KEY = 'id'

async def ensure_media_index() -> Any:
    
    try:
        index = await client.get_index(MEDIA_INDEX_NAME)
    except Exception:
        index = await client.create_index(uid=MEDIA_INDEX_NAME, primary_key=MEDIA_PRIMARY_KEY)
    await index.update_searchable_attributes(["title", "filename", "platform", "tags.name", "owner_name"])
    await index.update_filterable_attributes(["platform", "owner_id"])
    
    return index


async def index_media(documents: List[Dict[str, Any]]) -> Dict[str, Any]:
    index = await ensure_media_index()
    return await index.add_documents(documents)


async def delete_media(document_id: Union[int, str]) -> Dict[str, Any]:
    index = await ensure_media_index()
    return await index.delete_document(document_id)


async def search_media(
    query: str,
    filters: str = "",
    limit: int = 20,
    offset: int = 0
) -> Dict[str, Any]:
    
    await ensure_media_index()
    
    index = await client.get_index(MEDIA_INDEX_NAME)
    
    return await index.search(
        query=query or "",
        filter=filters or None,
        limit=limit,
        offset=offset
    )