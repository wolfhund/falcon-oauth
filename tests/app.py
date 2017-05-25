import falcon

from falcon_oauth.oauth2.views.authorization import AuthorizationCodeGrant


application = api = falcon.API()

authorization_code_grant = AuthorizationCodeGrant()
AUTHORIZATION_CODE_GRANT_PAGE_URI = '/oauth2/grant/authorizationcode/auth'
api.add_route(AUTHORIZATION_CODE_GRANT, authorization_code_grant)

