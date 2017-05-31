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

    def get_dynamic_scopes(self, request):
        # Place code here to dynamically determine the scopes
        # and return as a list
        try:
            request_scopes = request.scopes  # i.e. request.scopes="write,read"
        except AttributeError as error:
            raise TypeError from error
        else:
            scopes = [word.strip() for word in request_scopes.split(',')]
            return scopes

    def protected_resource_view(self, scopes=None):
        """Verify request and throw error if not valid.
        :param scopes: list A list containing the scopes for the page.
        :return: decorator
        """
        def decorator(f):
            @functools.wraps(f)
            def wrapper(self_obj, req, res, *args, **kwargs):
                """A wrapper for the called request method.
                :param self_obj: Object An self instance of the view.
                :param req: Object The request object instance of Falcon.
                :param res: Object The response object instance of Falcon.
                """
                # Get the list of scopes
                try:
                    scopes_list = get_dynamic_scopes(req)
                except TypeError:
                    scopes_list = scopes

                valid, r = self._resource_endpoint.verify_request(
                        req.uri, 
                        req.method, 
                        req.stream.read(), 
                        req.headers, 
                        scopes
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
