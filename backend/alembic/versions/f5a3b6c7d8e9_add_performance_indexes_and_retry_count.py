"""add_performance_indexes_and_retry_count

Revision ID: f5a3b6c7d8e9
Revises: e8f9a1b2c3d4
Create Date: 2025-10-19 11:08:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f5a3b6c7d8e9'
down_revision = 'e8f9a1b2c3d4'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add retry_count column to jobs table
    op.add_column('jobs', sa.Column('retry_count', sa.String(), nullable=False, server_default='0'))
    
    # Create composite indexes on jobs table for performance
    op.create_index('ix_job_user_status', 'jobs', ['user_id', 'status'])
    op.create_index('ix_job_status_started', 'jobs', ['status', 'started_at'])
    
    # Create composite indexes on sessions table for performance
    op.create_index('ix_session_user_expires', 'sessions', ['user_id', 'expires_at'])
    op.create_index('ix_session_expires', 'sessions', ['expires_at'])


def downgrade() -> None:
    # Drop indexes
    op.drop_index('ix_session_expires', table_name='sessions')
    op.drop_index('ix_session_user_expires', table_name='sessions')
    op.drop_index('ix_job_status_started', table_name='jobs')
    op.drop_index('ix_job_user_status', table_name='jobs')
    
    # Drop retry_count column
    op.drop_column('jobs', 'retry_count')
