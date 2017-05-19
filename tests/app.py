import falcon

from falcon_oauth.oauth2.views.authorization import Authenticate


application = api = falcon.API()

authenticate = Authenticate()
AUTH_PAGE_URI = '/oauth2/auth'
api.add_route(AUTH_PAGE_URI, authenticate)

