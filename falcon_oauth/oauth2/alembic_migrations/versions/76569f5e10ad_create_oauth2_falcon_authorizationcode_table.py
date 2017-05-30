"""Create authorization_code table

Revision ID: 76569f5e10ad
Revises: 4753c0947717
Create Date: 2017-05-17 12:54:02.795368

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '76569f5e10ad'
down_revision = '4753c0947717'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'oauth2_falcon_authorizationcode',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('client_id', sa.Integer, sa.ForeignKey('oauth2_falcon_client.id'), nullable=False),
        sa.Column('user_id', sa.Integer, sa.ForeignKey('oauth2_falcon_user.id'), nullable=True),
        sa.Column('scopes', sa.Text, nullable=False),
        sa.Column('code', sa.String(100), unique=True),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=False),
    )


def downgrade():
    op.drop_table('oauth2_falcon_authorizationcode')
