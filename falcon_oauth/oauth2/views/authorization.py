"""Authorization handler."""
import falcon
from falcon_oauth.oauth2.validators.oauth2_request_validator import OAuth2RequestValidator, server


class Authorization(object):
    """
    Handle for endpoint: /oauth2/auth. Authorization code grant
    """
    def __init__(self):
        self.server = server

    def on_post(self, req, res):
        """Create access token.

        :param req: Object A Falcon Request instance.
        :param res: Object A Falcon Response instance.
        """
        headers, body, status_code = self.server.create_token_response(
            req.uri,
            http_method=req.method,
            body=req.stream.read(),
            headers=req.headers,
        )
        res.headers = headers
        res.body = body
        res.status_code = status_code

    def on_get(self, req, res):
        import logging
        logging.getLogger(__name__).debug('test')
        try:
            scopes, credentials = self._authorization_endpoint.validate_authorization_request(
                req.uri,
                http_method=req.method,
                body=req.stream.read(),
                headers=req.headers
            )
        except Exception as e:
            res.body = '{"error": "server error"}'
            res.status = falcon.HTTP_500
        else:
            res.body = '<h1>Authorize access to %s</h1>' % req.params.get('client_id')
            res.body += '<form method="POST" action="/authorize">'
            for scope in scopes or []:
                res.body += '<input type="checkbox" name="scopes" ' + 'value="%s"/> %s' % (scope, scope)
            res.body += '<input type="submit" value="Authorize"/>'
            res.body += '</form>'
            res.content_type = 'text/html'
            res.status = falcon.HTTP_200
            print(credentials)
