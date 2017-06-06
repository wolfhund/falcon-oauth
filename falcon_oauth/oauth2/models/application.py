"""
Application oauth2 model, see

https://oauthlib.readthedocs.io/en/latest/oauth2/server.html#client-or-consumer
"""
import sqlalchemy as sa
from sqlalchemy.orm import relationship
from falcon_oauth.utils.database import Base


class Application(Base):  # pylint: disable=too-few-public-methods
    """Application model for OAuth2
    """
    __tablename__ = 'oauth2_falcon_application'
    # TODO: check that this attribute is being called or if it needs
    # a method to do it according to SQLAlchemy
    allowed_response_types = ('code', 'token')

    id = sa.Column(sa.Integer, primary_key=True)
    client_id = sa.Column(sa.String(100), nullable=False, unique=True)
    user_id = sa.Column(
        sa.Integer,
        sa.ForeignKey('oauth2_falcon_user.id'),
        nullable=True
    )
    user = relationship('User')
    grant_type = sa.Column(sa.String(18), nullable=False)
    response_type = sa.Column(sa.String(4), nullable=False)
    scopes = sa.Column(sa.Text, nullable=True)
    # ex: "modify_profile,access_billing
    default_scopes = sa.Column(sa.Text, nullable=False)
    # ex: "http://example.com/auth,http://oauth.amazon.com/"
    redirect_uris = sa.Column(sa.Text, nullable=True)
    default_redirect_uri = sa.Column(sa.Text, nullable=False)
