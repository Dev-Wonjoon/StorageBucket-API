from alembic import command
from alembic.config import Config
from core.config import Settings
import asyncio, logging, traceback
from alembic import command, config as al_cfg

settings = Settings()

cfg_path = settings.base_dir / "alembic.ini"

def _upgrade_to_head() -> None:
    cfg = al_cfg.Config(str(cfg_path))
    cfg.set_main_option("sqlalchemy.url", settings.database_url_cfg)
    cfg.set_main_option("script_location", str(cfg_path.with_suffix("")))
    logging.basicConfig(level=logging.INFO)

    try:
        command.upgrade(cfg, "head")
    except Exception:
        logging.error("Alembic upgrade failed!\n%s", traceback.format_exc())
        raise    
    
async def upgrade_to_head() -> None:
    await asyncio.to_thread(_upgrade_to_head)