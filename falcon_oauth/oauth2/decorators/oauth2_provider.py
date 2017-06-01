"""Decorator for the OAuth2 protection.
"""
import functools
import falcon
from falcon_oauth.oauth2.validators import server


def get_dynamic_scopes(request):
    # Place code here to dynamically determine the scopes
    # and return as a list
    try:
        request_scopes = request.scopes  # i.e. request.scopes="write,read"
    except AttributeError:
        raise
    else:
        scopes = [word.strip() for word in request_scopes.split(',')]
        return scopes


def add_params(obj, attributes_dict):
    """Add client, user and scopes to instantiated object as attributes.
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


class OAuth2ProviderDecorator(object):  # pylint: disable=too-few-public-methods
    """OAuth2 decorator to protect endpoints in views."""
    def __init__(self, resource_endpoint):
        self._resource_endpoint = resource_endpoint

    def protected_resource_view(self, scopes=None):
        """Verify request and throw error if not valid.
        :param scopes: list A list containing the scopes for the page.
        :return: decorator
        """
        def decorator(method):
            """Decorator method to handle a function.
            :param method: def A method defined when calling the decorator.
            """
            @functools.wraps(method)
            def wrapper(*args, **kwargs):
                """Wrapper method for decorator.

                :param *args: Variable length argument list.
                :param **kwargs: Arbitrary keyword arguments.
                """
                falcon_req = args[1]
                falcon_res = args[2]

                try:
                    scopes_list = self.get_dynamic_scopes(falcon_req)
                except AttributeError:
                    scopes_list = scopes

                valid, oauthlib_req = self._resource_endpoint.verify_request(
                    falcon_req.uri,
                    falcon_req.method,
                    falcon_req.stream.read(),
                    falcon_req.headers,
                    scopes_list
                )

                # For convenient parameter access in the view
                add_params(falcon_req, {
                    'client': oauthlib_req.client,
                    'user': oauthlib_req.user,
                    'scopes': oauthlib_req.scopes
                })

                if valid:
                    return method(*args, **kwargs)
                else:
                    falcon_res.body = '{"error": "forbidden"}'
                    falcon_res.status = falcon.HTTP_403

            return wrapper

        return decorator

provider = OAuth2ProviderDecorator(server)  # pylint: disable=invalid-name
