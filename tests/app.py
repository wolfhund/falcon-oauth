import falcon

from falcon_oauth.oauth2.views.authorization_code_view import AuthorizationCodeView


application = api = falcon.API()

authorization_code_view = AuthorizationCodeView()
AUTHORIZATION_CODE_VIEW_PAGE_URI = '/oauth2/authorizationcode/auth'
api.add_route(AUTHORIZATION_CODE_GRANT, authorization_code_view)

