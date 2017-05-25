from .app import AUTH_PAGE_URI


def test_auth_page_serves(webtest_app):
    # TODO status should not be 500
    resp = webtest_app.get(AUTH_PAGE_URI, status=500)
    assert resp.status_int == 500
