import falcon
from falcon_oauth.oauth2.validators.oauth2_request_validator import OAuth2RequestValidator, server


# Handles requests to /token
class Token(object):

    def __init__(self):
        # Using the server from previous section
        self._token_endpoint = server

    def on_post(self, req, res):
        # If you wish to include request specific extra credentials for
        # use in the validator, do so here.
        credentials = {'foo': 'bar'}
        try:
            headers, body, status = self._token_endpoint.create_token_response(
                req.uri, 
                http_method=req.method, 
                body=req.stream.read(), 
                headers=req.headers, 
                credentials=credentials
            )
        except Exception as e:
            res.body = '{"error": "server error"}'
            res.status = falcon.HTTP_500
            raise
        else:
            res.headers = headers
            res.body = body
            res.status_code = status
