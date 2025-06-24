from alembic import command
from alembic.config import Config
from core.config import Settings
import asyncio, logging, traceback
from alembic import command, config as al_cfg

settings = Settings()

cfg_path = settings.base_dir / "alembic.ini"

def _upgrade_to_head() -> None:
    cfg = al_cfg.Config(str(cfg_path))
    print(f"[DEBUG] Alembic uses URL = {settings.database_url_cfg!r}")
    cfg.set_main_option("sqlalchemy.url", settings.database_url_cfg)
    cfg.set_main_option("script_location", str(cfg_path.with_suffix("")))

    try:
        command.upgrade(cfg, "head")
        print("_upgrade_to_head RETURN()")
    except Exception:
        logging.error("Alembic upgrade failed!\n%s", traceback.format_exc())
        raise
    
async def upgrade_to_head() -> None:
    if settings.database_type == 'postgresql':
        await asyncio.to_thread(_upgrade_to_head)