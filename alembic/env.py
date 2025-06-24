from logging.config import fileConfig
from sqlalchemy import pool
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine
from sqlmodel import SQLModel
from alembic import context
from core.config import Settings
import sys, asyncio


settings = Settings()

sys.path.append(str(settings.base_dir))
async_engine: AsyncEngine = create_async_engine(
    settings.database_url,
    poolclass=pool.NullPool,
    future=True,
)
config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = SQLModel.metadata
config.set_main_option('sqlalchemy.url', settings.database_url_cfg)

def run_migrations_offline() -> None:
    """alembic upgrade --sql` 같은 오프라인 모드"""
    url = settings.database_url_cfg
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
    )

    with context.begin_transaction():
        context.run_migrations()


async def run_migrations_online() -> None:
    async with async_engine.connect() as conn:
        def do_run_migrations(connection):
            context.configure(
                connection=connection,
                target_metadata=target_metadata,
                compare_type=True,
            )
            with context.begin_transaction():
                context.run_migrations()
        
        await conn.run_sync(do_run_migrations)


if context.is_offline_mode():
    run_migrations_offline()
else:
    asyncio.run(run_migrations_online())
