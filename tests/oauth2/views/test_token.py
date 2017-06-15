# pylint: disable=invalid-name,missing-docstring
"""
tests that the token endpoint works fine
"""
import json
from datetime import datetime, timedelta, timezone
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


def test_token_page_serves(webtest_app):
    resp = webtest_app.post(TOKEN_URI, status=400)  # pylint: disable=unused-variable


def test_token_page_sends_401_with_bad_code(webtest_app, model_factory, clear_database):
    clear_database()
    app = model_factory.save_application(
        client_id='test',
        grant_type='authorization_code')

    request_params = {'grant_type': app.grant_type,
                      'code': 'test',
                      'client_id': app.client_id}
    resp = webtest_app.post(TOKEN_URI, request_params, status=401)  # pylint: disable=unused-variable

def test_token_page_fails_with_expired_code(webtest_app, model_factory, clear_database):
    clear_database()
    auth_code = model_factory.save_authorization_code(
        scopes='default_scope',
        code='testcode',
        expires_at=datetime.now(tz=timezone.utc) - timedelta(hours=1))
    auth_code.application.grant_type = 'authorization_code'
    auth_code.application.redirect_uris = 'http://test.redirect.com'

    request_params = {'grant_type': auth_code.application.grant_type,
                      'code': auth_code.code,
                      'client_id': auth_code.application.client_id,
                      'redirect_uri': auth_code.application.redirect_uris,
                      'scope': auth_code.application.default_scopes}
    resp = webtest_app.post(TOKEN_URI, request_params, status=401)  # pylint: disable=unused-variable

def test_token_page_sends_token_with_good_request(webtest_app, model_factory, clear_database):
    clear_database()
    auth_code = model_factory.save_authorization_code(
        scopes='default_scope',
        code='testcode')
    auth_code.application.grant_type = 'authorization_code'
    auth_code.application.redirect_uris = 'http://test.redirect.com'

    request_params = {'grant_type': auth_code.application.grant_type,
                      'code': auth_code.code,
                      'client_id': auth_code.application.client_id,
                      'redirect_uri': auth_code.application.redirect_uris,
                      'scope': auth_code.application.default_scopes}
    resp = webtest_app.post(TOKEN_URI, request_params)
    assert resp.status_code == 200
    resp_data = json.loads(resp.body.decode('utf-8'))
    assert 'access_token' in resp_data.keys()
    assert 'expires_in' in resp_data.keys()
    assert 'token_type' in resp_data.keys()
    assert 'scope' in resp_data.keys()
    assert 'refresh_token' in resp_data.keys()
