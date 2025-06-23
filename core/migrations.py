from alembic import command
from alembic.config import Config
from pathlib import Path
from core.config import Settings

settings = Settings()

cfg_path = settings.base_dir / "alembic.ini"

def upgrade_to_head() -> None:
    cfg = Config(str(cfg_path))
    cfg.set_main_option("sqlalchemy.url", settings.database_url)
    cfg.set_main_option(
        "script_location", str(cfg_path.with_suffix(""))
    )
    command.upgrade(cfg, "head")