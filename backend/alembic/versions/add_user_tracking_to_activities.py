"""Add user tracking and custom instructions to activities

Revision ID: add_user_tracking
Revises: create_user_tables
Create Date: 2024-01-20

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers
revision = 'add_user_tracking'
down_revision = 'create_user_tables'
branch_labels = None
depends_on = None

def upgrade() -> None:
    # Add columns to etkinlikler table
    op.add_column('etkinlikler', sa.Column('custom_instructions', sa.Text(), nullable=True))
    op.add_column('etkinlikler', sa.Column('created_by_id', postgresql.UUID(as_uuid=True), nullable=True))
    op.add_column('etkinlikler', sa.Column('created_by_username', sa.String(100), nullable=True))
    op.add_column('etkinlikler', sa.Column('created_by_fullname', sa.String(200), nullable=True))

    # Add foreign key constraint for etkinlikler
    op.create_foreign_key(
        'fk_etkinlikler_created_by',
        'etkinlikler',
        'users',
        ['created_by_id'],
        ['id'],
        ondelete='SET NULL'
    )

    # Add columns to gunluk_planlar table
    op.add_column('gunluk_planlar', sa.Column('created_by_id', postgresql.UUID(as_uuid=True), nullable=True))
    op.add_column('gunluk_planlar', sa.Column('created_by_username', sa.String(100), nullable=True))
    op.add_column('gunluk_planlar', sa.Column('created_by_fullname', sa.String(200), nullable=True))

    # Add foreign key constraint for gunluk_planlar
    op.create_foreign_key(
        'fk_gunluk_planlar_created_by',
        'gunluk_planlar',
        'users',
        ['created_by_id'],
        ['id'],
        ondelete='SET NULL'
    )

    # Create indexes for better query performance
    op.create_index('idx_etkinlikler_created_by_id', 'etkinlikler', ['created_by_id'])
    op.create_index('idx_gunluk_planlar_created_by_id', 'gunluk_planlar', ['created_by_id'])

def downgrade() -> None:
    # Drop indexes
    op.drop_index('idx_gunluk_planlar_created_by_id', 'gunluk_planlar')
    op.drop_index('idx_etkinlikler_created_by_id', 'etkinlikler')

    # Drop foreign key constraints
    op.drop_constraint('fk_gunluk_planlar_created_by', 'gunluk_planlar', type_='foreignkey')
    op.drop_constraint('fk_etkinlikler_created_by', 'etkinlikler', type_='foreignkey')

    # Drop columns from gunluk_planlar
    op.drop_column('gunluk_planlar', 'created_by_fullname')
    op.drop_column('gunluk_planlar', 'created_by_username')
    op.drop_column('gunluk_planlar', 'created_by_id')

    # Drop columns from etkinlikler
    op.drop_column('etkinlikler', 'created_by_fullname')
    op.drop_column('etkinlikler', 'created_by_username')
    op.drop_column('etkinlikler', 'created_by_id')
    op.drop_column('etkinlikler', 'custom_instructions')