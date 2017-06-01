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

    def _get_dynamic_scopes(self, request):
        # Place code here to dynamically determine the scopes
        # and return as a list
        try:
            request_scopes = request.scopes  # i.e. request.scopes="write,read"
        except AttributeError as error:
            raise TypeError from error
        else:
            scopes = [word.strip() for word in request_scopes.split(',')]
            return scopes

    def _add_params(self, obj, attributes_dict):
        """Add dictionary pair of key and value to instantiated object as attributes.
        :param obj: Object An instance of the object.
        :param attributes_dict: dict A dictionary of attributes with values.
        """
        obj.client = lambda: None
        obj.user = lambda: None
        obj.scopes = lambda: None

        for key, value in attributes_dict.items():
            if key == 'client':
                setattr(obj.client, key, value)
            elif key == 'user':
                setattr(obj.user, key, value)
            else:
                setattr(obj.scopes, key, value)

    def protected_resource_view(self, scopes=None):
        """Verify request and throw error if not valid.
        :param scopes: list A list containing the scopes for the page.
        :return: decorator
        """
        def decorator(method):
            """
            """
            @functools.wraps(method)
            def wrapper(self_obj, falcon_req, falcon_res, *args, **kwargs):
                """A wrapper for the called request method.
                :param self_obj: Object An self instance of the view.
                :param falcon_req: Object The request object instance of Falcon.
                :param falcon_res: Object The response object instance of Falcon.
                """
                # Get the list of scopes
                try:
                    scopes_list = self._get_dynamic_scopes(falcon_req)
                except TypeError:
                    scopes_list = scopes

                valid, oauthlib_req = self._resource_endpoint.verify_request(
                    falcon_req.uri, 
                    falcon_req.method, 
                    falcon_req.stream.read(), 
                    falcon_req.headers, 
                    scopes
                )
                # For convenient parameter access in the view
                self._add_params(falcon_req, {
                    'client': oauthlib_req.client,
                    'user': oauthlib_req.user,
                    'scopes': oauthlib_req.scopes
                })

                if valid:
                    return method(self_obj, falcon_req, falcon_res)
                else:
                    # Framework specific HTTP 403
                    falcon_res.body = '{"error": "forbidden"}'
                    falcon_res.status = falcon.HTTP_403
            return wrapper
        return decorator

provider = OAuth2ProviderDecorator(server)
