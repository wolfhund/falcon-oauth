import json
from tests.app import TOKEN_URI


def test_not_authorized_without_client_id(webtest_app):
    resp = webtest_app.post(
        TOKEN_URI,
        params={'grant_type': 'client_credentials'},
        status=401)

    assert resp.body == b'{"error": "invalid_client"}'


def test_not_authorized_with_incorrect_client_id(webtest_app):
    resp = webtest_app.post(
        TOKEN_URI,
        params={'grant_type': 'client_credentials', 'client_id': 'incorrect'},
        status=401)

    assert resp.body == b'{"error": "invalid_client"}'


def test_authorized_with_correct_client(clear_database, model_factory, webtest_app):
    clear_database()
    user = model_factory.save_user()
    app = model_factory.save_application(
        user_id=user.id)
    resp = webtest_app.post(
        TOKEN_URI,
        params={'grant_type': 'client_credentials', 'client_id': app.client_id},
        status=200)

    assert 'access_token' in json.loads(resp.body.decode('utf-8'))
