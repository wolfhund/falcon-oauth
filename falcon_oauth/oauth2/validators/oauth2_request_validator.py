""" OAuth 2 Web Application Server which is an OAuth provider configured
Authorization Code, Refresh Token grants and for dispensing Bearer Tokens.
"""
from datetime import datetime, timedelta, timezone
import logging
from oauthlib.oauth2 import RequestValidator, Server
from sqlalchemy.orm.exc import NoResultFound
from falcon_oauth.oauth2.models import Application, User, AuthorizationCode, BearerToken
from falcon_oauth.utils.database import Session


class OAuth2RequestValidator(RequestValidator):
    """OAuth2 Request Validator class for Authorization grant flow."""
    def __init__(self):
        self.expires_in = 3600  # seconds

    def _get_user(self, client_id):
        """Get User model related to Application model.

        :param client_id: str The hash string of the application.
        :return: Object SQLAlchemy instance of User model.
        """
        client = self._get_client(client_id)
        user = False
        try:
            user = User.query.get(
                User.id == client.user_id
            ).one()
        except NoResultFound:
            return False

        return user

    def _get_client(self, client_id):  # pylint: disable=no-self-use
        """Get Application instance by given client_id hash

        :param client_id: Object An SQLAlchemy instance of Application model.
        :return: Object The Application instance model.
        """
        try:
            client = Application.query.filter(
                Application.client_id == client_id
            ).one()
        except NoResultFound:
            return False

        return client

    def _get_authorization_code(self, client, code):  # pylint: disable=no-self-use
        authorization_code = False

        try:
            authorization_code = AuthorizationCode.query.filter(
                AuthorizationCode.application_id == client.id,
                AuthorizationCode.code == code,
            ).one()
        except NoResultFound:
            return False

        return authorization_code

    def _get_bearer_token(self, refresh_token=None, access_token=None):  # pylint: disable=no-self-use
        if refresh_token is not None and access_token is not None:
            return False
        if refresh_token is None and access_token is None:
            return False
        bearer_token = None

        try:
            if refresh_token is not None:
                bearer_token = BearerToken.query.filter(
                    BearerToken.refresh_token == refresh_token
                ).one()
            else:
                bearer_token = BearerToken.query.filter(
                    BearerToken.access_token == access_token
                ).one()
        except NoResultFound:
            return False

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

    def validate_redirect_uri(self, client_id, redirect_uri,
                              request, *args, **kwargs):
        # Is the client allowed to use the supplied redirect_uri? i.e. has
        # the client previously registered this EXACT redirect uri.
        request.client = request.client or self._get_client(client_id)

        client = request.client
        if client:
            redirect_uris_list = [
                uri.strip() for uri in client.redirect_uris.split(',')
            ]

        return redirect_uri in redirect_uris_list

    def get_default_redirect_uri(self, client_id, request, *args, **kwargs):
        # The redirect used if none has been supplied.
        # Prefer your clients to pre register a redirect uri rather than
        # supplying one on each authorization request.
        request.client = request.client or self._get_client(client_id)
        redirect_uri = request.client.default_redirect_uri
        logging.getLogger(__name__).debug('Found default redirect uri %r', redirect_uri)
        return redirect_uri

    def validate_scopes(self, client_id, scopes, client, request, *args, **kwargs):
        # Is the client allowed to access the requested scopes?
        request.client = client or self._get_client(client_id)
        client_scopes = [scope.strip() for scope in request.client.scopes.split(',')]
        # TODO: log if scopes is not a list of strings
        return set(client_scopes).issuperset(set(scopes))

    def get_default_scopes(self, client_id, request, *args, **kwargs):
        # Scopes a client will authorize for if none are supplied in the
        # authorization request.
        request.client = request.client or self._get_client(client_id)
        default_scopes = [scope.strip() for scope in request.client.default_scopes.split(',')]
        logging.getLogger(__name__).debug('Found default scopes %r', default_scopes)
        return default_scopes

    def validate_response_type(self, client_id, response_type, client, request,
                               *args, **kwargs):
        # Clients should only be allowed to use one type of response type, the
        # one associated with their one allowed grant type.
        # In this case it must be "code".
        request.client = client or self._get_client(client_id)
        return response_type in request.client.allowed_response_types

    def save_authorization_code(self, client_id, code, request, *args,
                                **kwargs):
        # Remember to associate it with request.scopes, request.redirect_uri
        # request.client, request.state and request.user_id
        # ( the last is passed in post_authorization credentials,
        # i.e. { 'user': request.user_id} )
        client = request.client or self._get_client(client_id)
        authorization_code = AuthorizationCode(
            application_id=client.id,
            user_id=None,
            scopes=request.scopes,
            code=request.code,
            expires_at=(datetime.now(tz=timezone.utc) +
                        timedelta(seconds=self.expires_in)))
        Session.add(authorization_code)  # pylint: disable=no-member

    def authenticate_client(self, request, *args, **kwargs):
        # Whichever authentication method suits you, HTTP Basic might work
        logging.getLogger(__name__).debug('Authenticate client %r', request.client_id)
        client = self._get_client(request.client_id)
        if not client:
            logging.getLogger(__name__).debug('Authenticate client failed, client not found.')
            return False

        request.client = client

        if (hasattr(request.client, 'client_secret') and
                request.client.client_secret != request.client_secret):
            logging.getLogger(__name__).debug('Authenticate client failed, secret not match.')
            return False

        logging.getLogger(__name__).debug('Authenticate client success.')
        return True

    def authenticate_client_id(self, client_id, request, *args, **kwargs):
        # Don't allow public (non-authenticated) clients
        if client_id is None:
            client_id = request.client_id

        logging.getLogger(__name__).debug('Authenticate client %r.', client_id)
        client = request.client or self._get_client(client_id)
        if not client:
            logging.getLogger(__name__).debug('Authenticate failed, client not found.')
            return False

        # attach client on request for convenience
        request.client = client
        return True

    def validate_code(self, client_id, code, client, request, *args, **kwargs):
        # Validate the code belongs to the client. Add associated scopes,
        # state and user to request.scopes and request.user_id.
        # TODO: verify that this logic is correct
        client = client or self._get_client(client_id)
        if not client:
            logging.getLogger(__name__).warning('No client given')
            return False
        authorization_code = self._get_authorization_code(client, code)
        if not authorization_code:
            logging.getLogger(__name__).warning('No authorization code provided')
            return False
        if datetime.now(tz=timezone.utc) > authorization_code.expires_at:
            logging.getLogger(__name__).warning('authorization: %s expired', authorization_code.id)
            return False
        authorized_scopes = authorization_code.scopes.split(',')
        request.user = authorization_code.user
        request.state = kwargs.get('state', None)
        request.scopes = list(set(request.scopes or []).intersection(authorized_scopes))
        request.claims = kwargs.get('claims', None)
        return True

    def confirm_redirect_uri(self, client_id, code, redirect_uri, client,
                             *args, **kwargs):
        # You did save the redirect uri with the authorization code right?
        try:
            allowed_redirect_uris = client.redirect_uris.split(',')
        except AttributeError:
            logging.getLogger(__name__).warning(
                'redirect uris: %(redirect_uris)s invalid for client_id: %(client_id)s',
                {'redirect_uris': client.redirect_uris, 'client_id': client.client_id})
            return False
        return redirect_uri in allowed_redirect_uris

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
        if grant_type == 'password' and self._get_user(client_id):
            logging.getLogger(__name__).warning('Tried to connect with password grant'
                                                ' with a client_id: %s', client_id)
            return False

        default_grant_types = (
            'authorization_code', 'password',
            'client_credentials', 'refresh_token')

        if grant_type not in default_grant_types:
            logging.getLogger(__name__).warning('grant_type: %s incorrect', grant_type)
            return False

        if grant_type == 'client_credentials':
            if not hasattr(client, 'user_id'):
                logging.getLogger(__name__).warning('Tried to connect with client grant'
                                                    ' without a client_id')
                return False
            request.user = client.user

        return True

    def save_bearer_token(self, token, request, *args, **kwargs):
        # Remember to associate it with request.scopes, request.user and
        # request.client. The two former will be set when you validate
        # the authorization code. Don't forget to save both the
        # access_token and the refresh_token and set expiration for the
        # access_token to now + expires_in seconds.
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
        scopes = ','.join([x.strip() for x in token['scope'].split(' ')])
        bearer_token = BearerToken(
            application_id=request.client.id,
            user_id=request.user.id,
            scopes=scopes,
            access_token=token['access_token'],
            refresh_token=token.get('refresh_token'),
            expires_at=(datetime.now(tz=timezone.utc) +
                        timedelta(seconds=token['expires_in'])))
        Session.add(bearer_token)  # pylint: disable=no-member
        logging.getLogger(__name__).debug('New token stored: %s', bearer_token.id)

        return request.client.default_redirect_uri

    def invalidate_authorization_code(self, client_id, code, request, *args, **kwargs):
        # Authorization codes are use once, invalidate it when a Bearer token
        # has been acquired.
        client = request.client or self._get_client(client_id)
        authorization_code = self._get_authorization_code(client, code)
        Session.delete(authorization_code)  # pylint: disable=no-member
        logging.getLogger(__name__).debug('Authorization code invalidated')

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
        logging.getLogger(__name__).debug('Validate bearer token %r', token)
        bearer_token = self._get_bearer_token(access_token=token)
        if not bearer_token:
            msg = 'Bearer token not found.'
            request.error_message = msg
            logging.getLogger(__name__).debug(msg)
            return False

        # validate expires
        if bearer_token.expires_at is not None and \
                datetime.now(tz=timezone.utc) > bearer_token.expires_at:
            msg = 'Bearer token is expired.'
            request.error_message = msg
            logging.getLogger(__name__).debug(msg)
            return False

        # validate scopes
        if scopes and not set(bearer_token.scopes.split(',')) & set(scopes):
            msg = 'Bearer token scope not valid.'
            request.error_message = msg
            logging.getLogger(__name__).debug(msg)
            return False

        request.access_token = bearer_token.access_token
        request.user = bearer_token.user
        request.scopes = scopes

        request.client = bearer_token.application
        return True

    # Token refresh request

    def get_original_scopes(self, refresh_token, request, *args, **kwargs):
        # Obtain the token associated with the given refresh_token and
        # return its scopes, these will be passed on to the refreshed
        # access token if the client did not specify a scope during the
        # request.
        logging.getLogger(__name__).debug('Obtaining scope of refreshed token.')
        bearer_token = self._get_bearer_token(refresh_token=refresh_token)
        if not bearer_token:
            return False
        return bearer_token.scopes

validator = OAuth2RequestValidator()  # pylint: disable=invalid-name
server = Server(validator)  # pylint: disable=invalid-name
