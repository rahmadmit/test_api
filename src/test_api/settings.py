from pydantic import BaseSettings
from .db.postgres import PostgresURL

class AppSettings(BaseSettings):
    postgres_url: PostgresURL
    root_path: str = "/api"

settings = AppSettings()