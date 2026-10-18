"""add_target_link_to_orders

Revision ID: a3c7e1d5b9f2
Revises: 514fddede0ed
Create Date: 2026-10-18 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a3c7e1d5b9f2'
down_revision: Union[str, None] = '514fddede0ed'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # nullable: orders created before this revision have no stored link
    op.add_column(
        'orders',
        sa.Column('target_link', sa.String(length=512), nullable=True, comment='لینک هدف سفارش (پست تلگرام)'),
    )


def downgrade() -> None:
    op.drop_column('orders', 'target_link')
