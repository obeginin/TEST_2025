"""Initial migration

Revision ID: 0001
Revises: 
Create Date: 2025-01-22 15:20:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '0001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create wallets table
    op.create_table('wallets',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('uuid', sa.String(length=36), nullable=False),
        sa.Column('balance', sa.DECIMAL(precision=15, scale=2), nullable=False),
        sa.Column('currency', sa.String(length=3), nullable=False),
        sa.Column('status', sa.String(length=20), nullable=False),
        sa.Column('version', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes for wallets table
    op.create_index(op.f('ix_wallets_uuid'), 'wallets', ['uuid'], unique=True)
    op.create_index(op.f('ix_wallets_status'), 'wallets', ['status'], unique=False)
    
    # Create transactions table
    op.create_table('transactions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('wallet_id', sa.Integer(), nullable=False),
        sa.Column('operation_type', sa.String(length=20), nullable=False),
        sa.Column('amount', sa.DECIMAL(precision=15, scale=2), nullable=False),
        sa.Column('balance_before', sa.DECIMAL(precision=15, scale=2), nullable=False),
        sa.Column('balance_after', sa.DECIMAL(precision=15, scale=2), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('reference_id', sa.String(length=100), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['wallet_id'], ['wallets.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes for transactions table
    op.create_index(op.f('ix_transactions_wallet_id'), 'transactions', ['wallet_id'], unique=False)
    op.create_index(op.f('ix_transactions_operation_type'), 'transactions', ['operation_type'], unique=False)
    op.create_index(op.f('ix_transactions_reference_id'), 'transactions', ['reference_id'], unique=False)
    op.create_index(op.f('ix_transactions_created_at'), 'transactions', ['created_at'], unique=False)


def downgrade() -> None:
    # Drop indexes for transactions table
    op.drop_index(op.f('ix_transactions_created_at'), table_name='transactions')
    op.drop_index(op.f('ix_transactions_reference_id'), table_name='transactions')
    op.drop_index(op.f('ix_transactions_operation_type'), table_name='transactions')
    op.drop_index(op.f('ix_transactions_wallet_id'), table_name='transactions')
    
    # Drop transactions table
    op.drop_table('transactions')
    
    # Drop indexes for wallets table
    op.drop_index(op.f('ix_wallets_status'), table_name='wallets')
    op.drop_index(op.f('ix_wallets_uuid'), table_name='wallets')
    
    # Drop wallets table
    op.drop_table('wallets')
