"""Token view file."""
from falcon_oauth.oauth2.validators import server
from falcon.util import get_http_status

from .utils import handle_error

class Token(object):  # pylint: disable=too-few-public-methods
    """Token view class. Handle requests to /oauth2/token"""
    def __init__(self):
        self._token_endpoint = server

    def on_post(self, req, res):
        """Generate token response.

        :param req: Object A Falcon Request instance.
        :param res: Object A Falcon Response instance.
        """
        # If you wish to include request specific extra credentials for
        # use in the validator, do so here.
        credentials = {'foo': 'bar'}
        try:
            headers, body, status = self._token_endpoint.create_token_response(
                req.uri,
                http_method=req.method,
                body=req.stream.read(),
                headers=req.headers,
                credentials=credentials)
        except Exception:  # pylint: disable=broad-except
            handle_error(req, res)
        else:
            res.headers = headers
            res.body = body
            res.status = get_http_status(status)
