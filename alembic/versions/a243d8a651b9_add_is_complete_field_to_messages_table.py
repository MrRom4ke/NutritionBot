from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'a243d8a651b9'
down_revision = '4169a3dadbb0'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Добавляем поле is_complete в таблицу messages
    op.add_column('messages', sa.Column('is_complete', sa.Boolean(), nullable=True))


def downgrade() -> None:
    # Удаляем поле is_complete при откате миграции
    op.drop_column('messages', 'is_complete')
