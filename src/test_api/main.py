import logging
from datetime import datetime
from typing import Optional

import requests
from fastapi import APIRouter, Depends, FastAPI
from fastapi.openapi.utils import get_openapi
from fastapi_utils.cbv import cbv
from fastapi_utils.tasks import repeat_every
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.sql import and_, desc

from test_api.parser.html_parser import CustomParser
from test_api.parser.model import NewsSqlModel

from .db.postgres import PostgresClient, get_db
from .settings import settings
from .util import postgres_session_dependency

router = APIRouter()

logger = logging.getLogger()


@cbv(router)
class Router:
    session: "AsyncSession" = Depends(postgres_session_dependency, use_cache=False)

    @router.get("/news")
    async def get_news(self, from_: datetime, to: datetime):
        all_news = (
            await self.session.execute(
                select(NewsSqlModel).where(
                    and_(
                        NewsSqlModel.publish_date >= from_,
                        NewsSqlModel.publish_date <= to,
                    )
                )
            )
        ).scalars().all()
        return [str(n) for n in all_news]


app = FastAPI()
app.state.postgres_client = PostgresClient(settings.postgres_url)
app.include_router(router=router, prefix="/metro")


@app.on_event("startup")
@repeat_every(seconds=600, raise_exceptions=True)
async def startup():
    try:
        session: AsyncSession = await get_db(settings.postgres_url)
        last_news: Optional[NewsSqlModel] = (
            await session.execute(
                select(NewsSqlModel).order_by(desc(NewsSqlModel.publish_date))
            )
        ).scalars().first()

        last_news = datetime(1, 1, 1, 1, 1, 1) if last_news is None else last_news.publish_date

        response = requests.get(
            settings.metro_news_url, headers={"User-Agent": "*"}
        )
        parser = CustomParser(last_news)
        parser.feed(response.text)
        await parser.builder.upload(session)
    finally:
        await session.close()


app.openapi_schema = get_openapi(title="Test-API", version="0.0.1", routes=app.routes)
