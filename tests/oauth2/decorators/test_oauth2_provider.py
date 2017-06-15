import json
from tests.app import PROTECTED_ENDPOINT_URI


def test_no_access_without_auth(webtest_app):
    resp = webtest_app.get(PROTECTED_ENDPOINT_URI, status=403)

    assert resp.body == b'{"error": "forbidden"}'


def test_no_access_with_bad_scope(webtest_app, clear_database, model_factory):
    clear_database()
    scope = 'bad_scope'
    webtest_app.authenticate(scopes=scope)
    resp = webtest_app.get(PROTECTED_ENDPOINT_URI, status=403)

    assert resp.body == b'{"error": "forbidden"}'


def test_access_with_auth(webtest_app, clear_database, model_factory):
    clear_database()
    scope = 'default_get'
    webtest_app.authenticate(scopes=scope)
    resp = webtest_app.get(PROTECTED_ENDPOINT_URI, status=200)
    resp_dict = json.loads(resp.body.decode('utf-8'))

    assert resp_dict['client'] == webtest_app.application.client_id
    assert resp_dict['user'] == webtest_app.user.id
    assert resp_dict['scopes'] == [scope]


def test_no_access_with_bad_ip(webtest_app, clear_database, model_factory):
    clear_database()
    scope = 'bad_scope'
    webtest_app.authenticate(scopes=scope)
    resp = webtest_app.post(PROTECTED_ENDPOINT_URI,
                            headers={'HTTP-CLIENT-ID': '7.7.7.7'},
                            status=403)

    assert resp.body == b'{"error": "forbidden"}'


def test_no_access_with_bad_scope_good_ip(webtest_app, clear_database, model_factory):
    clear_database()
    scope = 'bad_scope'
    webtest_app.authenticate(scopes=scope)
    resp = webtest_app.post(PROTECTED_ENDPOINT_URI,
                            headers={'HTTP-CLIENT-ID': '8.8.8.8'},
                            status=403)

    assert resp.body == b'{"error": "forbidden"}'


def test_access_with_good_ip(webtest_app, clear_database, model_factory):
    clear_database()
    scope = 'default_post'
    webtest_app.authenticate(scopes=scope)
    resp = webtest_app.post(PROTECTED_ENDPOINT_URI,
                            headers={'HTTP-CLIENT-ID': '8.8.8.8'},
                            status=200)

    resp_dict = json.loads(resp.body.decode('utf-8'))

    assert resp_dict['client'] == webtest_app.application.client_id
    assert resp_dict['user'] == webtest_app.user.id
    assert resp_dict['scopes'] == [scope]
