"""
some utils functions used by multiple views
"""
import logging
import falcon


def handle_error(req, resp):
    """
    logs an exception which occured with its traceback in the logger
    and generates the response

    :param: req the request object given by sqlalchemy
    :param: resp the response object given by sqlalchemy
    """
    logging.getLogger(__name__).exception(
        'Server 500: token creation unsuccessful from ip: %s',
        req.remote_addr)  # pylint: disable=broad-except
    resp.body = '{"error": "server error"}'
    resp.status = falcon.HTTP_500
