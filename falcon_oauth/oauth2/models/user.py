"""
the user model in oauth, see

https://oauthlib.readthedocs.io/en/latest/oauth2/server.html#user-or-resource-owner
"""
import sqlalchemy as sa
from falcon_oauth.utils.database import Base


class User(Base):  # pylint: disable=too-few-public-methods
    """User model class based on Django 1.9.
    See https://docs.djangoproject.com/en/1.9/ref/contrib/auth/
    """
    __tablename__ = 'oauth2_falcon_user'

    id = sa.Column(sa.Integer, primary_key=True)
    username = sa.Column(sa.String(30), nullable=False)
    first_name = sa.Column(sa.String(30), nullable=True)
    last_name = sa.Column(sa.String(30), nullable=True)
    email = sa.Column(sa.String(254), nullable=False)
    password = sa.Column(sa.String(255), nullable=False)
    is_superuser = sa.Column(sa.Boolean(), nullable=False)
    is_staff = sa.Column(sa.Boolean, nullable=False)
    is_active = sa.Column(sa.Boolean, nullable=False)
    last_login = sa.Column(sa.DateTime(timezone=True), nullable=False)
    date_joined = sa.Column(sa.DateTime(timezone=True), nullable=False)
