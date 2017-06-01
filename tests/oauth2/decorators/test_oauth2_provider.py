import json
from tests.app import PROTECTED_ENDPOINT_URI


def test_no_access_without_auth(webtest_app):
    resp = webtest_app.get(PROTECTED_ENDPOINT_URI, status=403)

    assert resp.body == b'{"error": "forbidden"}'


def test_no_access_with_bad_scope(webtest_app, clear_database, model_factory):
    clear_database()
    scope = 'bad_scope'
    user = model_factory.save_user()
    app = model_factory.save_application(user_id=user.id, default_scopes=scope)
    webtest_app.authenticate(application_id=app.id, user_id=user.id, scopes=scope)
    resp = webtest_app.get(PROTECTED_ENDPOINT_URI, status=403)

    assert resp.body == b'{"error": "forbidden"}'


def test_access_with_auth(webtest_app, clear_database, model_factory):
    clear_database()
    scope = 'default_get'
    user = model_factory.save_user()
    app = model_factory.save_application(user_id=user.id, default_scopes=scope)
    webtest_app.authenticate(application_id=app.id, user_id=user.id, scopes=scope)
    resp = webtest_app.get(PROTECTED_ENDPOINT_URI, status=200)
    resp_dict = json.loads(resp.body.decode('utf-8'))

    assert resp_dict['client'] == app.client_id
    assert resp_dict['user'] == user.id
    assert resp_dict['scopes'] == [scope]


def test_no_access_with_bad_ip(webtest_app, clear_database, model_factory):
    clear_database()
    scope = 'bad_scope'
    user = model_factory.save_user()
    app = model_factory.save_application(user_id=user.id, default_scopes=scope)
    webtest_app.authenticate(application_id=app.id, user_id=user.id, scopes=scope)
    resp = webtest_app.post(PROTECTED_ENDPOINT_URI,
                           headers={'HTTP-CLIENT-ID': '7.7.7.7'},
                           status=403)

    assert resp.body == b'{"error": "forbidden"}'


def test_no_access_with_bad_scope_good_ip(webtest_app, clear_database, model_factory):
    clear_database()
    scope = 'bad_scope'
    user = model_factory.save_user()
    app = model_factory.save_application(user_id=user.id, default_scopes=scope)
    webtest_app.authenticate(application_id=app.id, user_id=user.id, scopes=scope)
    resp = webtest_app.post(PROTECTED_ENDPOINT_URI,
                           headers={'HTTP-CLIENT-ID': '8.8.8.8'},
                           status=403)

    assert resp.body == b'{"error": "forbidden"}'


def test_access_with_good_ip(webtest_app, clear_database, model_factory):
    clear_database()
    scope = 'default_post'
    user = model_factory.save_user()
    app = model_factory.save_application(user_id=user.id, default_scopes=scope)
    webtest_app.authenticate(application_id=app.id, user_id=user.id, scopes=scope)
    resp = webtest_app.post(PROTECTED_ENDPOINT_URI,
                           headers={'HTTP-CLIENT-ID': '8.8.8.8'},
                           status=200)

    resp_dict = json.loads(resp.body.decode('utf-8'))

    assert resp_dict['client'] == app.client_id
    assert resp_dict['user'] == user.id
    assert resp_dict['scopes'] == [scope]
