import falcon

from falcon_oauth.oauth2.views.authorization import Authorization
from falcon_oauth.oauth2.views.token import Token


application = api = falcon.API()

authorization_view = Authorization()
AUTHORIZATION_URI = '/oauth2/authorize/'
api.add_route(AUTHORIZATION_URI, authorization_view)

token_view = Token()
TOKEN_URI = '/oauth2/token/'
api.add_route(TOKEN_URI, token_view)
