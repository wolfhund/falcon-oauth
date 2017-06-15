import json
from tests.app import AUTHORIZATION_URI


def test_not_authorized_without_client_id(webtest_app):
    resp = webtest_app.post(
        AUTHORIZATION_URI,
        params={'grant_type': 'client_credentials'},
        status=401)

    assert resp.body == b'{"error": "invalid_client"}'


def test_not_authorized_with_incorrect_client_id(webtest_app):
    resp = webtest_app.post(
        AUTHORIZATION_URI,
        params={'grant_type': 'client_credentials', 'client_id': 'incorrect'},
        status=401)

    assert resp.body == b'{"error": "invalid_client"}'


def test_authorized_with_correct_client(clear_database, model_factory, webtest_app):
    clear_database()
    app = model_factory.save_application()
    resp = webtest_app.post(
        AUTHORIZATION_URI,
        params={'grant_type': 'client_credentials', 'client_id': app.client_id},
        status=200)

    assert 'access_token' in json.loads(resp.body.decode('utf-8'))


def test_authorization_get_no_client(webtest_app):
    resp = webtest_app.get(AUTHORIZATION_URI, status=401)
    assert resp.body == b'{"error": "invalid_client"}'


def test_authorization_get_wrong_client(webtest_app):
    resp = webtest_app.get(AUTHORIZATION_URI, {'client_id': 'invalid'}, status=401)
    assert resp.body == b'{"error": "invalid_client"}'


def test_authorization_get_without_grant(clear_database, model_factory, webtest_app):
    clear_database()
    app = model_factory.save_application()
    resp = webtest_app.get(AUTHORIZATION_URI, {'client_id': app.client_id}, status=400)
    assert resp.body == b'{"error": "unsupported_grant_type"}'


def test_authorization_get(clear_database, model_factory, webtest_app):
    clear_database()
    app = model_factory.save_application()
    webtest_app.get(
        AUTHORIZATION_URI,
        {'response_type': 'code', 'client_id': app.client_id},
        status=200)
