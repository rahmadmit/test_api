from fastapi import Request

from .db.postgres import PostgresClient

async def postgres_session_dependency(request: "Request"):
    postgres_client: PostgresClient = request.app.state.postgres_client
    async with postgres_client.session() as session:
        yield session