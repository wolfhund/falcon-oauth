import falcon
from falcon_oauth.oauth2.validators.oauth2_request_validator import server
from oauthlib.oauth2 import BackendApplicationServer
from falcon_oauth.oauth2.validators.oauth2_request_validator import OAuth2RequestValidator


class Authorization(object):
    """
    Handle for endpoint: /oauth2/auth. Authorization code grant
    """
    def __init__(self):
        validator = OAuth2RequestValidator()
        self.server = BackendApplicationServer(validator)

    def on_post(self, req, res):
        ### client credentials grant ###
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
            raise
        else:
            print(scopes, credentials)

        ###

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
