from alembic import command
from alembic.config import Config
from core.config import Settings
import asyncio

settings = Settings()

cfg_path = settings.base_dir / "alembic.ini"

def _upgrade_to_head() -> None:
    cfg = Config(str(cfg_path))
    cfg.set_main_option("sqlalchemy.url", settings.database_url)
    cfg.set_main_option(
        "script_location", str(cfg_path.with_suffix(""))
    )
    command.upgrade(cfg, "head")
    
async def upgrade_to_head() -> None:
    await asyncio.to_thread(_upgrade_to_head)