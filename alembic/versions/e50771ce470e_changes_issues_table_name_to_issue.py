"""Initial migration

Revision ID: e50771ce470e
Revises:
Create Date: 2024-04-20 15:14:49.284583

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e50771ce470e'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.rename_table('issues', 'issue', schema='project_management')

def downgrade():
    op.rename_table('issue', 'issues', schema='project_management')
