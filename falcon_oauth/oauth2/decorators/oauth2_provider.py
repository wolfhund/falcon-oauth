"""Decorator for the OAuth2 protection.
"""
import functools
import falcon
from falcon_oauth.oauth2.validators import server


class OAuth2ProviderDecorator(object):
    """OAuth2 decorator to protect endpoints in views.
    """

    def __init__(self, resource_endpoint):
        self._resource_endpoint = resource_endpoint

    def protected_resource_view(self, scopes=None):
        def decorator(f):
            @functools.wraps(f)
            def wrapper(self_obj, req,res, *args, **kwargs):
                # Get the list of scopes
                try:
                    scopes_list = scopes(req)
                except TypeError:
                    scopes_list = scopes

                valid, r = self._resource_endpoint.verify_request(
                        req.uri, 
                        req.method, 
                        req.stream.read(), 
                        req.headers, 
                        scopes_list
                )

                # For convenient parameter access in the view
                #add_params(req, {
                #    'client': r.client,
                #    'user': r.user,
                #    'scopes': r.scopes
                #})
                if valid:
                    return f(self_obj, req, res)
                else:
                    # Framework specific HTTP 403
                    res.body = '{"error": "forbidden"}'
                    res.status = falcon.HTTP_403
            return wrapper
        return decorator

provider = OAuth2ProviderDecorator(server)
