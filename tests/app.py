import falcon

from falcon_oauth.oauth2.views.authorization import Authorization
from falcon_oauth.oauth2.views.token import Token
from falcon_oauth.oauth2.decorators.oauth2_provider import provider

application = api = falcon.API()  # pylint: disable=invalid-name

authorization_view = Authorization()  # pylint: disable=invalid-name
AUTHORIZATION_URI = '/oauth2/authorize/'
api.add_route(AUTHORIZATION_URI, authorization_view)

token_view = Token()  # pylint: disable=invalid-name
TOKEN_URI = '/oauth2/token/'
api.add_route(TOKEN_URI, token_view)


def _post_scopes(req):
    if req.headers.get('HTTP_CLIENT_ID', '') == '8.8.8.8':
        return ['default_post']
    else:
        return []


class ProtectedEndpoint(object):

    """
    endpoint to test the decorator which validates authentication
    """

    @provider.protected_resource_view(scopes=['default_get'])
    def on_get(self, req, resp):
        resp.body = '{"ok": "ok"}'

    @provider.protected_resource_view(scopes=_post_scopes)
    def on_post(self, req, resp):
        resp.body = '{"ok": "ok"}'


protected_endpoint = ProtectedEndpoint()  # pylint: disable=invalid-name
PROTECTED_ENDPOINT_URI = '/protected_resource'
api.add_route(PROTECTED_ENDPOINT_URI, protected_endpoint)
