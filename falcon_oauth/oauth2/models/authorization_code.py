"""
the authorization code model, see

https://oauthlib.readthedocs.io/en/latest/oauth2/server.html#authorization-code
"""
import sqlalchemy as sa
from falcon_oauth.utils.database import Base


class AuthorizationCode(Base):  # pylint: disable=too-few-public-methods
    """AuthorizationCode model for OAuth2.
    """
    __tablename__ = 'authorization_code'

    id = sa.Column(sa.Integer, primary_key=True)
    client_id = sa.Column(sa.Integer, sa.ForeignKey('client.id'), nullable=False)
    user_id = sa.Column(sa.Integer, sa.ForeignKey('user.id'), nullable=True)
    scopes = sa.Column(sa.Text, nullable=False)
    code = sa.Column(sa.String(100), unique=True)
    expires_at = sa.Column(sa.DateTime(timezone=True), nullable=False)
