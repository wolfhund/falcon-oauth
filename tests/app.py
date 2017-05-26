import falcon

from falcon_oauth.oauth2.views.authorization import Authorization


application = api = falcon.API()

authorization_view = AuthorizationCodeView()
AUTHORIZATION_URI = '/oauth2/authorize/'
api.add_route(AUTHORIZATION_URI, authorization_view)
