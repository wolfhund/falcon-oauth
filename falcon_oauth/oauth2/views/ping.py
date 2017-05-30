import falcon
from falcon_oauth.oauth2.decorators.oauth2_provider import provider


class Ping(object):

    @provider.protected_resource_view(scopes=['read', 'write'])
    def on_get(self, req, res):
        res.body = '{"res":"pong"}'
        res.status_code = falcon.HTTP_200
