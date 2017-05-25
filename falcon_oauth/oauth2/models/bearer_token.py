"""
bearer token model, see

https://oauthlib.readthedocs.io/en/latest/oauth2/server.html#bearer-token-oauth-2-standard-token
"""
import sqlalchemy as sa
from falcon_oauth.utils.database import Base


class BearerToken(Base):  # pylint: disable=too-few-public-methods
    """BearerToken model for OAuth2.
    """
    __tablename__ = 'bearer_token'

    id = sa.Column(sa.Integer, primary_key=True)
    client_id = sa.Column(sa.Integer, sa.ForeignKey('client.id'), nullable=False)
    user_id = sa.Column(sa.Integer, sa.ForeignKey('user.id'), nullable=True)
    scopes = sa.Column(sa.Text, nullable=False)
    access_token = sa.Column(sa.String(100), unique=True)
    refresh_token = sa.Column(sa.String(100), unique=True)
    expires_at = sa.Column(sa.DateTime(timezone=True), nullable=False)
