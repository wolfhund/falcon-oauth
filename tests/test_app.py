from .app import AUTH_PAGE_URI


def test_auth_page_serves(webtest_app):
    # TODO status should not be 500
    params = {
        'client_id': 'a4337bc45a8fc544c03f52dc550cd6e1e87021bc896588bd79e901e2',
        'state': 'xyz',
        'default_query_uri': 'http://localhost:8000/oauth2/callback',
        'response_type': 'code'
    }
    resp = webtest_app.get(AUTH_PAGE_URI, params=params, status=200)
    assert resp.status_int == 200
