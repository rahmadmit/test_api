from datetime import datetime
import logging
import requests

from fastapi import FastAPI, Depends, APIRouter
from fastapi_utils.tasks import repeat_every
from fastapi_utils.cbv import cbv
from fastapi.openapi.utils import get_openapi
from sqlalchemy.sql import text, desc, and_
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from test_api.parser.html_parser import CustomParser

from test_api.parser.model import NewsSqlModel

from .db.postgres import PostgresClient, get_db
from .util import postgres_session_dependency

from .settings import settings

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
                        NewsSqlModel.publish_date > from_,
                        NewsSqlModel.publish_date < to,
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
    logger.info("sus")
    try:
        session: AsyncSession = await get_db(settings.postgres_url)
        last_news = (
            await session.execute(
                select(NewsSqlModel).order_by(desc(NewsSqlModel.publish_date))
            )
        ).scalars().first()
        if last_news is None:
            last_news = datetime(1, 1, 1, 1, 1, 1)
        else:
            last_news = last_news.publish_date

        headers = {"User-Agent": "*"}
        response = requests.get(
            "https://mosday.ru/news/tags.php?metro", headers=headers
        )
        parser = CustomParser(last_news)
        parser.feed(response.text)
        await parser.builder.upload(session)
    finally:
        await session.close()


app.openapi_schema = get_openapi(title="Test-API", version="0.0.1", routes=app.routes)
