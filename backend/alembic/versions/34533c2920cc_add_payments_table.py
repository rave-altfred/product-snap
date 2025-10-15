"""add_payments_table

Revision ID: 34533c2920cc
Revises: 73f36f1f25f6
Create Date: 2025-10-15 13:10:55.567252

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '34533c2920cc'
down_revision = '73f36f1f25f6'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create payments table
    op.create_table(
        'payments',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('user_id', sa.String(), nullable=False),
        sa.Column('subscription_id', sa.String(), nullable=True),
        sa.Column('paypal_payment_id', sa.String(), nullable=True),
        sa.Column('paypal_subscription_id', sa.String(), nullable=True),
        sa.Column('amount', sa.Float(), nullable=False),
        sa.Column('currency', sa.String(), nullable=False),
        sa.Column('status', sa.String(), nullable=False),
        sa.Column('payment_method', sa.String(), nullable=False),
        sa.Column('description', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['subscription_id'], ['subscriptions.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_payments_id'), 'payments', ['id'], unique=False)
    op.create_index(op.f('ix_payments_user_id'), 'payments', ['user_id'], unique=False)
    op.create_index(op.f('ix_payments_paypal_payment_id'), 'payments', ['paypal_payment_id'], unique=False)
    op.create_index(op.f('ix_payments_paypal_subscription_id'), 'payments', ['paypal_subscription_id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_payments_paypal_subscription_id'), table_name='payments')
    op.drop_index(op.f('ix_payments_paypal_payment_id'), table_name='payments')
    op.drop_index(op.f('ix_payments_user_id'), table_name='payments')
    op.drop_index(op.f('ix_payments_id'), table_name='payments')
    op.drop_table('payments')
