"""fix_cancel_at_period_end_type

Revision ID: e8f9a1b2c3d4
Revises: 34533c2920cc
Create Date: 2025-10-19 10:58:55.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e8f9a1b2c3d4'
down_revision = '34533c2920cc'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Change cancel_at_period_end from String to Boolean
    # PostgreSQL requires explicit USING clause for type conversion
    op.execute("""
        ALTER TABLE subscriptions 
        ALTER COLUMN cancel_at_period_end 
        TYPE BOOLEAN 
        USING CASE 
            WHEN cancel_at_period_end IN ('true', 't', '1', 'yes', 'y', 'True', 'TRUE') THEN TRUE
            ELSE FALSE
        END
    """)
    
    # Set NOT NULL constraint
    op.alter_column('subscriptions', 'cancel_at_period_end',
                    existing_type=sa.Boolean(),
                    nullable=False,
                    server_default=sa.false())


def downgrade() -> None:
    # Revert to String type if needed
    op.alter_column('subscriptions', 'cancel_at_period_end',
                    existing_type=sa.Boolean(),
                    type_=sa.String(),
                    nullable=True,
                    server_default=None)
    
    # Convert boolean values to string
    op.execute("""
        UPDATE subscriptions 
        SET cancel_at_period_end = CASE 
            WHEN cancel_at_period_end::boolean THEN 'True'
            ELSE 'False'
        END
    """)
