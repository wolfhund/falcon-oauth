"""
Client oauth2 model, see

https://oauthlib.readthedocs.io/en/latest/oauth2/server.html#client-or-consumer
"""
import sqlalchemy as sa
from falcon_oauth.utils.database import Base


class Client(Base):  # pylint: disable=too-few-public-methods
    """Client model for OAuth2
    """
    __tablename__ = 'client'
    # TODO: check that this attribute is being called or if it needs
    # a method to do it according to SQLAlchemy
    allowed_response_types = ('code', 'token')

    id = sa.Column(sa.Integer, primary_key=True)
    client_id = sa.Column(sa.String(100), nullable=False, unique=True)
    user_id = sa.Column(sa.Integer, sa.ForeignKey('user.id'), nullable=True)
    grant_type = sa.Column(sa.String(18), nullable=False)
    response_type = sa.Column(sa.String(4), nullable=False)
    scopes = sa.Column(sa.Text, nullable=True)
    default_scopes = sa.Column(sa.Text, nullable=False)
    redirect_uris = sa.Column(sa.Text, nullable=True)
    default_redirect_uri = sa.Column(sa.Text, nullable=False)
