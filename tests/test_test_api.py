from datetime import datetime
from email.mime import base
from uuid import uuid4

import pytest
from fastapi import FastAPI
from httpx import AsyncClient
from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession
from test_api import __version__
from test_api.db.postgres import PostgresClient
from test_api.main import router
from test_api.parser.model import NewsSqlModel
from test_api.settings import settings

app = FastAPI()
app.state.postgres_client = PostgresClient(settings.postgres_url)
app.include_router(router, prefix="/metro")


def test_version():
    assert __version__ == "0.1.0"


@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"



@pytest.fixture(scope="session")
async def test_api():
    async with AsyncClient(app=app, base_url="http://test") as t_a:
        yield t_a


@pytest.fixture(scope="session")
async def db():
    client = PostgresClient(settings.postgres_url)
    async with client.session() as session:
        yield session


@pytest.fixture
async def get_news(db: AsyncSession):
    news = [
        NewsSqlModel(
            id=uuid4(), news="Test text", publish_date=datetime(2023, 7, 27, x, 0, 0)
        )
        for x in range(24)
    ]
    db.add_all(news)
    await db.commit()
    yield news

    await db.execute(delete(NewsSqlModel))

@pytest.mark.anyio
async def test_get_news(test_api: AsyncClient):
    from_ = datetime(2023, 7, 27, 10, 0, 0)
    to_ = datetime(2023, 7, 27, 15, 0, 0)
    response = await test_api.get(
        "/metro/news", params={"from_": from_, "to": to_}
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 6
