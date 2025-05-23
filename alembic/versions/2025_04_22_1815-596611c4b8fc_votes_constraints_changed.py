"""votes constraints changed

Revision ID: 596611c4b8fc
Revises: 9939ae9370ad
Create Date: 2025-04-22 18:15:00.991416

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '596611c4b8fc'
down_revision: Union[str, None] = '9939ae9370ad'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_unique_constraint('product_user', 'el_vote', ['product_id', 'user_id'])
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint('product_user', 'el_vote', type_='unique')
    # ### end Alembic commands ###
