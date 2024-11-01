"""Recreate entities table with ordered columns

Revision ID: f9c5a58921af
Revises: 420f43e2aa82
Create Date: 2024-11-01 09:25:57.122911

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'f9c5a58921af'
down_revision = '420f43e2aa82'
branch_labels = None
depends_on = None

def upgrade():
    # Создание новой таблицы entities с нужным порядком столбцов
    op.create_table(
        'entities',
        sa.Column('message_id', sa.UUID(), nullable=False),
        sa.Column('action', sa.String(), nullable=True),
        sa.Column('object', sa.String(), nullable=True),
        sa.Column('specific_object', sa.String(), nullable=True),
        sa.Column('location', sa.String(), nullable=True),
        sa.Column('quantity', sa.String(), nullable=True),
        sa.Column('size', sa.String(), nullable=True),
        sa.Column('conditions', sa.String(), nullable=True),
        sa.Column('duration', sa.String(), nullable=True),
        sa.Column('time', sa.String(), nullable=True),
        sa.Column('date', sa.String(), nullable=True),
        sa.Column('theme_id', sa.Integer(), sa.ForeignKey("topics.id", ondelete="SET NULL"), nullable=True),
        sa.ForeignKeyConstraint(['message_id'], ['messages.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('message_id')
    )

def downgrade():
    # Откат - удаление таблицы entities
    op.drop_table('entities')
