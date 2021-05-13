"""create user table

Revision ID: 28b495605c74
Revises: 
Create Date: 2021-05-12 21:43:17.194681

"""
from alembic import op
import sqlalchemy as sa

# Custom
from sqlalchemy import text


# revision identifiers, used by Alembic.
revision = '28b495605c74'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'users',
        sa.Column('id', sa.Integer, primary_key=True, unique_key=True),
        sa.Column('first_name', sa.String(255), nullable=False),
        sa.Column('last_name', sa.String(255), nullable=False),
        sa.Column('email', sa.String(255), nullable=False),
        sa.Column('phone', sa.String(50), nullable=False),
        sa.Column('password', sa.String(255), nullable=False),
        sa.Column('is_active', sa.BOOLEAN, default=False),
        sa.Column('is_deleted', sa.BOOLEAN, default=False),
        sa.Column('created_at', sa.TIMESTAMP, server_default=sa.func.current_timestamp()),
        sa.Column('updated_at', sa.TIMESTAMP, server_default=text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP')),
        sa.Column('deleted_at', sa.TIMESTAMP),
    )


def downgrade():
    pass
