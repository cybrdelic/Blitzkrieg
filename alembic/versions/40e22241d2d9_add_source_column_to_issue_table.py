"""Add source column to issue table

Revision ID: 40e22241d2d9
Revises: e50771ce470e
Create Date: 2024-04-22 16:00:46.781682

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '40e22241d2d9'
down_revision: Union[str, None] = 'e50771ce470e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    # Add 'source' column with ENUM type 'docs' and 'github'
    source_type = sa.Enum('docs', 'github', name='source_type')
    source_type.create(op.get_bind(), checkfirst=True)
    op.add_column('issue', sa.Column('source', source_type), schema='project_management')

def downgrade():
    # Remove 'source' column and ENUM type
    op.drop_column('issue', 'source', schema='project_management')
    sa.Enum(name='source_type').drop(op.get_bind(), checkfirst=True)
