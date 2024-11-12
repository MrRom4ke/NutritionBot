"""Add table EntityRequirement and link it to EntityModel

Revision ID: 779c60314129
Revises: f9c5a58921af
Create Date: 2024-11-04 10:51:20.086502

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '779c60314129'
down_revision = 'f9c5a58921af'
branch_labels = None
depends_on = None

def upgrade() -> None:
    # Создание таблицы entity_requirements
    op.create_table(
        'entity_requirements',
        sa.Column('id', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('action', sa.String, nullable=True),
        sa.Column('object', sa.String, nullable=True),
        sa.Column('required_fields', postgresql.ARRAY(sa.String), nullable=True),
        sa.Column('questions', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.UniqueConstraint('action', 'object', name='unique_action_object')
    )

    # Добавление столбца entity_requirements_id в таблицу entities
    op.add_column('entities', sa.Column('entity_requirements_id', sa.Integer, sa.ForeignKey('entity_requirements.id'), nullable=True))


def downgrade() -> None:
    # Удаление столбца entity_requirements_id из таблицы entities
    op.drop_column('entities', 'entity_requirements_id')

    # Удаление таблицы entity_requirements
    op.drop_table('entity_requirements')
