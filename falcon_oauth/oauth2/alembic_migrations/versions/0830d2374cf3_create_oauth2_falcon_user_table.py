"""Create user table. This model was based on User model of Django 1.9 version, 
see https://docs.djangoproject.com/en/1.9/ref/contrib/auth

Revision ID: 0830d2374cf3
Revises: 
Create Date: 2017-05-16 17:42:16.705468

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0830d2374cf3'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'oauth2_falcon_user',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('username', sa.String(30), nullable=False),
        sa.Column('first_name', sa.String(30), nullable=True),
        sa.Column('last_name', sa.String(30), nullable=True),
        sa.Column('email', sa.String(254), nullable=False),
        sa.Column('password', sa.String(255), nullable=False),
        sa.Column('is_superuser', sa.Boolean(), nullable=False),
        sa.Column('is_staff', sa.Boolean, nullable=False),
        sa.Column('is_active', sa.Boolean, nullable=False),
        sa.Column('last_login', sa.DateTime(timezone=True), nullable=False),
        sa.Column('date_joined', sa.DateTime(timezone=True), nullable=False),
    )


def downgrade():
    op.drop_table('oauth2_falcon_user')
