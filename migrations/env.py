import os
from logging.config import fileConfig

from alembic import context
from sqlalchemy import engine_from_config, pool

from app.infrastructure.config.settings import Settings
# Import all models so Alembic can detect them
from app.infrastructure.models import order, outbox  # noqa: F401
from app.infrastructure.models.base import BaseModel

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata
target_metadata = BaseModel.metadata

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def get_url():
    """Get database URL from environment variables or Settings"""
    # First, try to get DATABASE_URL directly
    db_url = os.getenv("POSTGRES_CONNECTION_STRING")
    if db_url:
        # Convert asyncpg URL to psycopg2 URL if needed
        if db_url.startswith("postgres://"):
            db_url = db_url.replace("postgres://", "postgresql+psycopg://", 1)
        elif db_url.startswith("postgresql+asyncpg://"):
            db_url = db_url.replace("postgresql+asyncpg://", "postgresql://", 1)
            config.set_main_option("sqlalchemy.url", db_url)
        return db_url

    # Otherwise, use Settings class which loads from .env file
    settings = Settings()

    # If db_url is set in settings, use it
    if settings.db_url:
        if settings.db_url.startswith("postgresql+asyncpg://"):
            return settings.db_url.replace("postgresql+asyncpg://", "postgresql://")
        return settings.db_url

    # Fall back to constructing from individual settings
    db_user = settings.postgres_user
    db_pass = settings.postgres_password
    db_host = settings.postgres_host
    db_port = settings.postgres_port
    db_name = settings.postgres_db

    return f"postgresql://{db_user}:{db_pass}@{db_host}:{db_port}/{db_name}"


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = get_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    configuration = config.get_section(config.config_ini_section)
    configuration["sqlalchemy.url"] = get_url()

    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
