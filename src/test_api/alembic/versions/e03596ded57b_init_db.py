"""init db

Revision ID: e03596ded57b
Revises: 
Create Date: 2023-07-27 18:05:23.613766

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision = "e03596ded57b"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "metro_news",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("news", sa.String(), nullable=False),
        sa.Column("publish_date", sa.TIMESTAMP(timezone=False), nullable=False),
        sa.Column("upload_date", sa.TIMESTAMP(timezone=False), nullable=False),
    )


def downgrade() -> None:
    op.drop_table("metro_news")
