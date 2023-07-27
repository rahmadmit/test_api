from pydantic import BaseSettings, HttpUrl
from .db.postgres import PostgresURL

class AppSettings(BaseSettings):
    postgres_url: PostgresURL
    metro_news_url: HttpUrl


settings = AppSettings()