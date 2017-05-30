import falcon
from oauthlib.oauth2 import BackendApplicationServer
from falcon_oauth.oauth2.validators.oauth2_request_validator import OAuth2RequestValidator


class OAuth2ProviderDecorator(object):

    def __init__(self, resource_endpoint):
        self._resource_endpoint = resource_endpoint

    def protected_resource_view(self, scopes=None):
        def decorator(f):
            @functools.wraps(f)
            def wrapper(req):
                # Get the list of scopes
                try:
                    scopes_list = scopes(req)
                except TypeError:
                    scopes_list = scopes

                valid, r = self._resource_endpoint.verify_request(
                        req.uri, 
                        http_method=req.method, 
                        body=req.stream.read(), 
                        headers=req.headers, 
                        scopes_list=scopes_list
                )

                # For convenient parameter access in the view
                add_params(req, {
                    'client': r.client,
                    'user': r.user,
                    'scopes': r.scopes
                })
                if valid:
                    return f(req)
                else:
                    # Framework specific HTTP 403
                    req.body = '{"error": "forbidden"}'
                    req.status_code = falcon.HTTP_403
            return wrapper
        return decorator

validator = OAuth2RequestValidator()
server = BackendApplicationServer(validator)
provider = OAuth2ProviderDecorator(server)
