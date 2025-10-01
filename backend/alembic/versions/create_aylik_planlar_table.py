"""create aylik_planlar table

Revision ID: create_aylik_planlar
Create Date: 2025-09-21

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'create_aylik_planlar'
down_revision = 'add_user_tracking_to_activities'
branch_labels = None
depends_on = None


def upgrade():
    # Create aylik_planlar table
    op.create_table('aylik_planlar',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('plan_adi', sa.String(length=500), nullable=False),
        sa.Column('yas_grubu', sa.String(length=50), nullable=False),
        sa.Column('ay', sa.String(length=20), nullable=False),
        sa.Column('yil', sa.Integer(), nullable=False),
        sa.Column('alan_becerileri', sa.JSON(), nullable=False),
        sa.Column('kavramsal_beceriler', sa.JSON(), nullable=False),
        sa.Column('egilimler', sa.JSON(), nullable=False),
        sa.Column('sosyal_duygusal_beceriler', sa.JSON(), nullable=False),
        sa.Column('degerler', sa.JSON(), nullable=False),
        sa.Column('okuryazarlik_becerileri', sa.JSON(), nullable=False),
        sa.Column('ogrenme_ciktilari', sa.JSON(), nullable=False),
        sa.Column('anahtar_kavramlar', sa.JSON(), nullable=False),
        sa.Column('degerlendirme', sa.JSON(), nullable=False),
        sa.Column('ogrenme_ogretme_yasantilari', sa.Text(), nullable=False),
        sa.Column('farklilastirma_zenginlestirme', sa.Text(), nullable=True),
        sa.Column('destekleme', sa.Text(), nullable=True),
        sa.Column('aile_toplum_katilimi', sa.Text(), nullable=True),
        sa.Column('custom_instructions', sa.Text(), nullable=True),
        sa.Column('ai_generated', sa.Boolean(), nullable=True, default=False),
        sa.Column('ai_model', sa.String(length=100), nullable=True),
        sa.Column('ai_prompt', sa.Text(), nullable=True),
        sa.Column('created_by', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('kazanim_ids', sa.JSON(), nullable=True),
        sa.Column('curriculum_ids', sa.JSON(), nullable=True),
        sa.ForeignKeyConstraint(['created_by'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_aylik_planlar_id'), 'aylik_planlar', ['id'], unique=False)


def downgrade():
    op.drop_index(op.f('ix_aylik_planlar_id'), table_name='aylik_planlar')
    op.drop_table('aylik_planlar')