import falcon
from falcon_oauth.oauth2.validators.oauth2_request_validator import server


class Authenticate(object):
    """
    Handle for endpoint: /oauth2/auth
    """
    def __init__(self):
        self._authorization_endpoint = server

    def on_post(self, req, res):
        pass

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

            res.body = 'you are on Authenticate get'
            res.status = falcon.HTTP_200
