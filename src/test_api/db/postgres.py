import asyncio
from contextlib import asynccontextmanager

from pydantic import PostgresDsn
from sqlalchemy.engine.url import URL
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_scoped_session,
    create_async_engine,
)
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import QueuePool


class PostgresURL(PostgresDsn):
    def sqlalchemy_url(self) -> URL:
        return URL(
            drivername="postgresql+asyncpg",
            username=self.user,
            password=self.password,
            host=self.host,
            port=self.port,
            database=self.path.split("/")[-1] if self.path else None,
        )


class PostgresClient:
    def __init__(self, postgres_dsn: PostgresURL) -> None:
        self._engine = create_async_engine(
            postgres_dsn.sqlalchemy_url(),
            future=True,
            poolclass=QueuePool,
            pool_pre_ping=True,
        )
        self._session_factory = async_scoped_session(
            session_factory=sessionmaker(
                bind=self._engine,
                autocommit=False,
                expire_on_commit=False,
                class_=AsyncSession,
            ),
            scopefunc=asyncio.current_task,
        )

    @asynccontextmanager
    async def session(self):
        async with self._session_factory() as session:
            yield session


async def get_db(postgres_dsn: PostgresURL):
    client = PostgresClient(postgres_dsn)
    async with client.session() as session:
        return session
