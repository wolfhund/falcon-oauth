"""Create client table

Revision ID: 18f04b58ee4c
Revises: 0830d2374cf3
Create Date: 2017-05-16 18:44:06.504208

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '18f04b58ee4c'
down_revision = '0830d2374cf3'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'client',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('client_id', sa.String(100), nullable=False, unique=True),
        sa.Column('user_id', sa.Integer, sa.ForeignKey('user.id'), nullable=True),
        sa.Column('grant_type', sa.String(18), nullable=False),
        sa.Column('response_type', sa.String(4), nullable=False),
        sa.Column('scopes', sa.Text, nullable=True),
        sa.Column('default_scopes', sa.Text, nullable=False),
        sa.Column('redirect_uris', sa.Text, nullable=True),
        sa.Column('default_redirect_uri', sa.Text, nullable=False),
    )


def downgrade():
    op.drop_table('client')
