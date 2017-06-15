"""
bearer token model, see

https://oauthlib.readthedocs.io/en/latest/oauth2/server.html#bearer-token-oauth-2-standard-token
"""
import sqlalchemy as sa
from sqlalchemy.orm import relationship
from falcon_oauth.utils.database import Base
from falcon_oauth.utils.database import Session


class BearerToken(Base):  # pylint: disable=too-few-public-methods
    """BearerToken model for OAuth2.
    """
    __tablename__ = 'oauth2_falcon_bearertoken'

    query = Session.query_property()
    id = sa.Column(sa.Integer, primary_key=True)
    application_id = sa.Column(
        sa.Integer,
        sa.ForeignKey('oauth2_falcon_application.id'),
        nullable=False)
    application = relationship('Application')
    user_id = sa.Column(
        sa.Integer,
        sa.ForeignKey('oauth2_falcon_user.id'),
        nullable=True
    )
    user = relationship('User')
    scopes = sa.Column(sa.Text, nullable=False)
    access_token = sa.Column(sa.String(100), unique=True, nullable=False)
    refresh_token = sa.Column(sa.String(100), unique=True, nullable=True)
    expires_at = sa.Column(sa.DateTime(timezone=True), nullable=False)
