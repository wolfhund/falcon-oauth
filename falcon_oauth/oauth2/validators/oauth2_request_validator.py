""" OAuth 2 Web Application Server which is an OAuth provider configured
Authorization Code, Refresh Token grants and for dispensing Bearer Tokens.
"""
import datetime
import pytz
from oauthlib.oauth2 import RequestValidator, WebApplicationServer
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.ext.declarative import declarative_base
from falcon_oauth.utils.database import get_engine_url
from ..models.client import Client
from ..models.user import User
from ..models.authorization_code import AuthorizationCode
from ..models.bearer_token import BearerToken

Base = declarative_base()


class OAuth2RequestValidator(RequestValidator):
    """OAuth2 Request Validator class for Authorization grant flow.
    """

    # Ordered roughly in order of appearance in the authorization grant flow

    # Pre- and post-authorization.
    def __init__(self):
        engine = create_engine(get_engine_url())
        Session = sessionmaker(bind=engine)  # pylint: disable=invalid-name
        self.session = Session()
        self.expires_in = 3600  # seconds

    def _get_user(self, client_id):
        client = self._get_client(client_id)
        user = None

        try:
            user = self.session.query(User).get(id == client.user_id)
        except NoResultFound:
            pass  # TODO: log error

        return user

    def _get_client(self, client_id):
        try:
            client = self.session.query(Client).filter(client_id == client_id)
        except NoResultFound:
            pass  # log error

        return client

    def _get_authorization_code(self, client):
        authorization_code = None

        try:
            authorization_code = self.session.query(AuthorizationCode).filter(
                client_id=client.client_id,
                user_id=client.user_id,
                code=client.code,
                scopes=client.scopes,
            )
        except NoResultFound:
            pass  # TODO: log error

        return authorization_code

    def _get_bearer_token(self, refresh_token=None, access_token=None):
        if refresh_token is not None and access_token is not None:
            raise ValueError('You should pass either a refresh_token, '
                             'either an access_token, not both')
        if refresh_token is None and access_token is None:
            raise ValueError('You should pass a refresh_token, '
                             'or an access_token, not nothing')
        bearer_token = None
        try:
            if refresh_token is not None:
                bearer_token = self.session.query(BearerToken).filter(refresh_token=refresh_token)
            else:
                bearer_token = self.session.query(BearerToken).filter(access_token=access_token)
        except NoResultFound:
            pass # TODO: log error
        return bearer_token

    def validate_client_id(self, client_id, request, *args, **kwargs):
        # Simple validity check, does client exist? Not banned?
        # log.debug('Validate client %r', client_id)
        client = request.client or self._get_client(client_id)
        if client:
            # attach client to request object
            request.client = client
            return True
        return False

    def validate_redirect_uri(self, client_id, redirect_uri, request, *args, **kwargs):
        # Is the client allowed to use the supplied redirect_uri? i.e. has
        # the client previously registered this EXACT redirect uri.
        request.client = request.client or self._get_client(client_id)

        client = request.client
        if client:
            redirect_uris_list = [uri.strip() for uri in client.redirect_uris.split(',')]

        return redirect_uri in redirect_uris_list

    def get_default_redirect_uri(self, client_id, request, *args, **kwargs):
        # The redirect used if none has been supplied.
        # Prefer your clients to pre register a redirect uri rather than
        # supplying one on each authorization request.
        request.client = request.client or self._get_client(client_id)
        redirect_uri = request.client.default_redirect_uri
        # TODO log.debug('Found default redirect uri %r', redirect_uri)
        return redirect_uri

    def validate_scopes(self, client_id, scopes, client, request, *args, **kwargs):
        # Is the client allowed to access the requested scopes?
        request.client = client or self._get_client(client_id)
        default_scopes = [scope.strip() for scope in request.client.default_scopes.split(',')]
        # TODO: log if scopes is not a list of strings
        return set(default_scopes).issuperset(set(scopes))

    def get_default_scopes(self, client_id, request, *args, **kwargs):
        # Scopes a client will authorize for if none are supplied in the
        # authorization request.
        request.client = request.client or self._get_client(client_id)
        default_scopes = [scope.strip() for scope in request.client.default_scopes.split(',')]
        # TODO  log.debug('Found default scopes %r', scopes)
        return default_scopes

    def validate_response_type(self, client_id, response_type, client, request, *args, **kwargs):
        # Clients should only be allowed to use one type of response type, the
        # one associated with their one allowed grant type.
        # In this case it must be "code".
        request.client = client or self._get_client(client_id)
        return response_type in request.client.allowed_response_types

    # Post-authorization

    def save_authorization_code(self, client_id, code, request, *args, **kwargs):
        # Remember to associate it with request.scopes, request.redirect_uri
        # request.client, request.state and request.user (the last is passed in
        # post_authorization credentials, i.e. { 'user': request.user}.
        authorization_code = AuthorizationCode(
            client_id=client_id,
            user_id=None,
            scopes=request.scopes,
            code=request.code,
            expires_at=(datetime.datetime.now(pytz.timezone('UTC')) +
                        datetime.timedelta(seconds=self.expires_in))
        )
        self.session.add(authorization_code)
        self.session.commit()
        # TODO: handle rollback in exception

    # Token request

    def authenticate_client(self, request, *args, **kwargs):
        # Whichever authentication method suits you, HTTP Basic might work
        # TODO: log.debug('Authenticate client %r', client_id)
        client = self._get_client(request.client_id)
        if not client:
            # TODO log.debug('Authenticate client failed, client not found.')
            return False

        request.client = client

        if (hasattr(request.client, 'client_secret') and
                request.client.client_secret != request.client_secret):
            # TODO log.debug('Authenticate client failed, secret not match.')
            return False

        # TODO log.debug('Authenticate client success.')
        return True

    def authenticate_client_id(self, client_id, request, *args, **kwargs):
        # Don't allow public (non-authenticated) clients
        if client_id is None:
            client_id = request.client_id

        # TODO log.debug('Authenticate client %r.', client_id)
        client = request.client or self._get_client(client_id)
        if not client:
            # TODO log.debug('Authenticate failed, client not found.')
            return False

        # attach client on request for convenience
        request.client = client
        return True

    def validate_code(self, client_id, code, client, request, *args, **kwargs):
        # Validate the code belongs to the client. Add associated scopes,
        # state and user to request.scopes and request.user.
        # TODO: verify that this logic is correct
        client = client or self._get_client(client_id)
        if not client:
            # TODO: log error
            return False
        authorization_code = self._get_authorization_code(client)
        if not authorization_code:
            # TODO: log error
            return False
        request.user = authorization_code.user
        request.state = kwargs.get('state', None)
        request.scopes = authorization_code.scopes
        request.claims = kwargs.get('claims', None)
        return True

    def confirm_redirect_uri(self, client_id, code, redirect_uri, client, request, *args, **kwargs):
        # You did save the redirect uri with the authorization code right?
        client = client or self._get_client(client_id)
        if not client:
            # TODO: log error
            return False
        authorization_code = self._get_authorization_code(client)
        if not authorization_code:
            # TODO: log error
            return False

        is_valid = self.validate_redirect_uri(client.client_id, redirect_uri, request)
        return is_valid and client.redirect_uri == redirect_uri

    def validate_grant_type(self, client_id, grant_type, client, request, *args, **kwargs):
        # Clients should only be allowed to use one type of grant.
        # In this case, it must be "authorization_code" or "refresh_token"
        """Ensure the client is authorized to use the grant type requested.
        It will allow any of the four grant types ('authorization_code',
        'password', 'client_credentials', 'refresh_token') by default.
        Implemented 'allowed_grant_types' for client object to authorize
        the request.
        It is suggested that 'allowed_grant_types' should contain at least
        'authorization_code' and 'refresh_token'.
        """
        if self._get_user(client_id) and grant_type == 'password':
            # TODO: log error
            return False

        default_grant_types = (
            'authorization_code', 'password',
            'client_credentials', 'refresh_token',
        )

        if grant_type not in default_grant_types:
            # TODO: log error
            return False

        if grant_type == 'client_credentials':
            if not hasattr(client, 'user_id'):
                # TODO: log error
                return False
            request.user = self._get_user(client_id)

        return True

    def save_bearer_token(self, token, request, *args, **kwargs):
        # Remember to associate it with request.scopes, request.user and
        # request.client. The two former will be set when you validate
        # the authorization code. Don't forget to save both the
        # access_token and the refresh_token and set expiration for the
        # access_token to now + expires_in seconds.
        # TODO log action
        """
        The parameter token is a dict, that looks like::
            {
                u'access_token': u'6JwgO77PApxsFCU8Quz0pnL9s23016',
                u'token_type': u'Bearer',
                u'expires_in': 3600,
                u'scope': u'email address'
            }
        The request is an object, that contains an user object and a
        client object.
        """
        scopes = ','.join([x.strip() for x in token['scope'].split(',')])
        bearer_token = BearerToken(
            client_id=request.client.client_id,
            user_id=request.user.user_id,
            scopes=scopes,
            access_token=token['access_token'],
            refresh_token=token['refresh_token'],
            expires_at=(datetime.datetime.utcnow() +
                        datetime.timedelta(seconds=token['expires_in']))
        )
        self.session.add(bearer_token)
        self.session.commit()

        return request.client.default_redirect_uri

    def invalidate_authorization_code(self, client_id, code, request, *args, **kwargs):
        # Authorization codes are use once, invalidate it when a Bearer token
        # has been acquired.
        # TODO: add logs and rollback in except
        client = request.client or self._get_client(client_id)
        authorization_code = self._get_authorization_code(client)
        self.session.delete(authorization_code)
        self.session.commit()

    # Protected resource request

    def validate_bearer_token(self, token, scopes, request):
        # Remember to check expiration and scope membership
        """Validate access token.
        :param token: A string of random characters
        :param scopes: A list of scopes
        :param request: The Request object passed by oauthlib
        The validation validates:
            1) if the token is available
            2) if the token has expired
            3) if the scopes are available
        """
        # TODO: log.debug('Validate bearer token %r', token)
        bearer_token = self._get_bearer_token(access_token=token)
        if not bearer_token:
            msg = 'Bearer token not found.'
            request.error_message = msg
            # TODO log.debug(msg)
            return False

        # validate expires
        if bearer_token.expires_at is not None and \
                datetime.datetime.utcnow() > bearer_token.expires_at:
            msg = 'Bearer token is expired.'
            request.error_message = msg
            # TODO: log.debug(msg)
            return False

        # validate scopes
        if scopes and not set(bearer_token.scopes) & set(scopes):
            msg = 'Bearer token scope not valid.'
            request.error_message = msg
            # TODO: log.debug(msg)
            return False

        request.access_token = bearer_token.access_token
        request.user = bearer_token.user_id
        request.scopes = scopes

        if hasattr(bearer_token, 'client_id'):
            request.client = self._get_client(bearer_token.client_id)
        return True

    # Token refresh request

    def get_original_scopes(self, refresh_token, request, *args, **kwargs):
        # Obtain the token associated with the given refresh_token and
        # return its scopes, these will be passed on to the refreshed
        # access token if the client did not specify a scope during the
        # request.
        # TODO: log.debug('Obtaining scope of refreshed token.')
        bearer_token = self._get_bearer_token(refresh_token=refresh_token)
        return bearer_token.scopes


validator = OAuth2RequestValidator()
server = WebApplicationServer(validator)