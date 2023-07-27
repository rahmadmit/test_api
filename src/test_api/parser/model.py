from datetime import date, datetime, time
from typing import List
from sqlmodel import SQLModel, Field, Column
from uuid import uuid4, UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.dialects.postgresql import UUID as UUID_Field, TIMESTAMP
from sqlalchemy.sql import functions


class NewsSqlModel(SQLModel, table=True):
    __tablename__ = "metro_news"
    __table_args__ = {"schema": "public"}

    id: UUID = Field(sa_column=Column(UUID_Field(as_uuid=True), primary_key=True))
    news: str
    publish_date: datetime = Field(sa_column=Column(TIMESTAMP(timezone=False)))
    upload_date: datetime = Field(sa_column=Column(TIMESTAMP(timezone=False)), default=functions.current_timestamp())

    def __str__(self) -> str:
        return f"{str(self.publish_date)} - {self.news}"

    def __repr__(self) -> str:
        return self.__str__()


class NewsModel:
    def __init__(self):
        self.date = None
        self.time = None
        self.timestamp = None
        self.text = None

    def __str__(self) -> str:
        return f"{str(self.timestamp)} - {self.text}"

    def __repr__(self) -> str:
        return self.__str__()

    def to_sql(self) -> NewsSqlModel:
        return NewsSqlModel(id=uuid4(), news=self.text, publish_date=self.timestamp)

class NewsBuilder:
    def __init__(self):
        self.news = NewsModel()
        self.news_list: List[NewsSqlModel] = []


    def set_date(self, d: date):
        self.news.date = d

    def set_time(self, t: time):
        self.news.time = t
        self.news.timestamp = datetime.combine(self.news.date, t)

    def set_text(self, t: str):
        self.news.text = t

    def push(self):
        self.news_list.append(self.news.to_sql())
        self.news = NewsModel()

    async def upload(self, session: AsyncSession) -> None:
        session.add_all(self.news_list)
        await session.commit()

    def check_date(self, last_date: datetime) -> bool:
        assert isinstance(last_date, datetime), f"shiiit, {last_date}"
        assert isinstance(self.news.timestamp, datetime), f"huinya, {self.news.timestamp, type(self.news.timestamp)}"
        return self.news.timestamp > last_date


# builder = NewsBuilder()