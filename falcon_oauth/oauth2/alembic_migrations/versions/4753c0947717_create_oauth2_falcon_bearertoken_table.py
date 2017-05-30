"""create bearer_token table

Revision ID: 4753c0947717
Revises: 18f04b58ee4c
Create Date: 2017-05-17 12:21:31.055227

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '4753c0947717'
down_revision = '18f04b58ee4c'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'oauth2_falcon_bearertoken',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('application_id', sa.Integer, sa.ForeignKey('oauth2_falcon_application.id'), nullable=False),
        sa.Column('user_id', sa.Integer, sa.ForeignKey('oauth2_falcon_user.id'), nullable=True),
        sa.Column('scopes', sa.Text, nullable=False),
        sa.Column('access_token', sa.String(100), unique=True),
        sa.Column('refresh_token', sa.String(100), unique=True),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=False),
    )


def downgrade():
    op.drop_table('oauth2_falcon_bearertoken')
