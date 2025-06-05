import asyncio
from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool
from alembic import context

# Это важно: импортируйте вашу Base и ваш асинхронный движок
from app.models import Base
from app.cruds import engine as async_db_engine # Импортируем ваш асинхронный движок, чтобы не конфликтовать с локальной переменной engine


# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
target_metadata = Base.metadata

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an actual DBAPI connection. By doing this,
    migrations can be run without a database connection present.
    For more complex operations (e.g., in testing different database
    types), a complete DBAPI connection is required.

    """
    url = config.get_main_option("sqlalchemy.url")
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

    In this scenario, we use our AsyncEngine.
    """
    connectable = async_db_engine # Ваш асинхронный движок из cruds.py

    # Определяем синхронную функцию, которую Alembic будет вызывать
    def do_run_migrations(connection):
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True, # Важно для autogenerate
        )
        with context.begin_transaction():
            context.run_migrations()

    # Определяем асинхронную функцию, которая будет получать подключение
    async def run_async_migrations():
        # Используем begin() для получения асинхронной транзакции
        async with connectable.begin() as connection:
            # Выполняем синхронные операции Alembic внутри асинхронной транзакции
            await connection.run_sync(do_run_migrations)

    # Запускаем асинхронную функцию
    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()