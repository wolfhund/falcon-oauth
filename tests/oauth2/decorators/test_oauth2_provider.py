from tests.app import PROTECTED_ENDPOINT_URI


def test_no_access_without_auth(webtest_app):
    resp = webtest_app.get(PROTECTED_ENDPOINT_URI, status=403)

    assert resp.body == b'{"error": "forbidden"}'


def test_no_access_with_bad_scope(webtest_app, clear_database, model_factory):
    clear_database()
    scope = 'bad_scope'
    user = model_factory.save_user()
    app = model_factory.save_application(user_id=user.id, default_scopes=scope)
    webtest_app.authenticate(application_id=app.id, scopes=scope)
    resp = webtest_app.get(PROTECTED_ENDPOINT_URI, status=403)

    assert resp.body == b'{"error": "forbidden"}'


def test_access_with_auth(webtest_app, clear_database, model_factory):
    clear_database()
    scope = 'default_get'
    user = model_factory.save_user()
    app = model_factory.save_application(user_id=user.id, default_scopes=scope)
    webtest_app.authenticate(application_id=app.id, scopes=scope)
    resp = webtest_app.get(PROTECTED_ENDPOINT_URI, status=200)

    assert resp.body == b'{"ok": "ok"}'


def test_no_access_with_bad_ip(webtest_app, clear_database, model_factory):
    clear_database()
    scope = 'bad_scope'
    user = model_factory.save_user()
    app = model_factory.save_application(user_id=user.id, default_scopes=scope)
    webtest_app.authenticate(application_id=app.id, scopes=scope)
    resp = webtest_app.get(PROTECTED_ENDPOINT_URI,
                           headers={'HTTP_CLIENT_ID': '7.7.7.7'},
                           status=403)

    assert resp.body == b'{"error": "forbidden"}'


def test_access_with_good_ip(webtest_app, clear_database, model_factory):
    clear_database()
    scope = 'bad_scope'
    user = model_factory.save_user()
    app = model_factory.save_application(user_id=user.id, default_scopes=scope)
    webtest_app.authenticate(application_id=app.id, scopes=scope)
    resp = webtest_app.get(PROTECTED_ENDPOINT_URI,
                           headers={'HTTP_CLIENT_ID': '8.8.8.8'},
                           status=403)

    assert resp.body == b'{"error": "forbidden"}'
