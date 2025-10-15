"""initial_schema

Revision ID: 73f36f1f25f6
Revises: 
Create Date: 2025-10-15 13:09:48.981711

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '73f36f1f25f6'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Database already has these tables from Base.metadata.create_all()
    # This migration just establishes the baseline
    pass


def downgrade() -> None:
    # Don't drop existing tables
    pass
