from datetime import date, datetime, time
from typing import List
from uuid import UUID, uuid4

from sqlalchemy.dialects.postgresql import TIMESTAMP
from sqlalchemy.dialects.postgresql import UUID as UUID_Field
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import functions
from sqlmodel import Column, Field, SQLModel


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

    def to_sql(self) -> NewsSqlModel:
        return NewsSqlModel(id=uuid4(), news=self.text, publish_date=self.timestamp)

class NewsBuilder:
    def __init__(self):
        self.news = NewsModel()
        self.upload_list: List[NewsSqlModel] = []


    def set_date(self, d: date):
        self.news.date = d

    def set_time(self, t: time):
        self.news.time = t
        self.news.timestamp = datetime.combine(self.news.date, t)

    def set_text(self, t: str):
        self.news.text = t

    def push(self):
        self.upload_list.append(self.news.to_sql())
        self.news = NewsModel()

    async def upload(self, session: AsyncSession) -> None:
        session.add_all(self.upload_list)
        await session.commit()

    def check_date(self, last_date: datetime) -> bool:
        return self.news.timestamp > last_date
