"""Authorization handler."""
import logging
import falcon
from oauthlib.oauth2.rfc6749.errors import (MissingClientIdError, InvalidClientIdError,
                                            MissingResponseTypeError)
from falcon_oauth.oauth2.validators.oauth2_request_validator import server

from .falcon_status_codes import FALCON_STATUS_CODES


class Authorization(object):
    """
    Handle for endpoint: /oauth2/auth. Authorization code grant
    """
    def __init__(self):
        self.server = server

    def on_post(self, req, resp):
        """Create access token.

        :param req: Object A Falcon Request instance.
        :param resp: Object A Falcon Response instance.
        """
        headers, body, status = self.server.create_token_response(
            req.uri,
            http_method=req.method,
            body=req.stream.read(),
            headers=req.headers,
        )
        resp.headers = headers
        resp.body = body
        resp.status = FALCON_STATUS_CODES[status]

    def on_get(self, req, resp):
        try:
            scopes, credentials = self.server.validate_authorization_request(  # pylint: disable=protected-access
                req.uri,
                http_method=req.method,
                body=req.stream.read(),
                headers=req.headers)
        except (MissingClientIdError, InvalidClientIdError):
            logging.exception('wrong or no client_id during authorization get')
            resp.body = '{"error": "invalid_client"}'
            resp.status = falcon.HTTP_401
        except MissingResponseTypeError:
            logging.exception('no response type in authorization get')
            resp.body = '{"error": "unsupported_grant_type"}'
            resp.status = falcon.HTTP_400
        except Exception:  # pylint: disable=broad-except
            logging.exception('Exception occured during authorization get')
            resp.body = '{"error": "server_error"}'
            resp.status = falcon.HTTP_500
        else:
            resp.body = ('<h1>Authorize access to {}</h1>'
                         .format(req.params.get('client_id')))
            resp.body += '<form method="POST" action="/authorize">'
            for scope in scopes or []:
                resp.body += ('<input type="checkbox" name="scopes" value="{}"/> {}'
                              .format(scope, scope))
            resp.body += '<input type="submit" value="Authorize"/>'
            resp.body += '</form>'
            resp.content_type = 'text/html'
            resp.status = falcon.HTTP_200
            print(credentials)
