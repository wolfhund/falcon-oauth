# pylint: disable=missing-docstring
from datetime import datetime, timedelta, timezone
import random
import string

import pytest
import factory
import factory.alchemy
from falcon_oauth.oauth2.models import Application, User, AuthorizationCode, BearerToken
from falcon_oauth.utils.database import Session

from webtest import TestApp
from .app import api


def _id_generator(size=20, chars=string.ascii_uppercase + string.digits):
    """
    generates a random string to simulate a token
    """
    return ''.join(random.choice(chars) for _ in range(size))


class BasicUser(factory.alchemy.SQLAlchemyModelFactory):  # pylint: disable=too-few-public-methods
    class Meta:  # pylint: disable=too-few-public-methods
        model = User
        sqlalchemy_session = Session

    username = 'testusr'
    email = 'test@user.com'
    password = 'default_password'
    is_superuser = False
    is_staff = False
    is_active = True
    date_joined = datetime.now(tz=timezone.utc)
    last_login = datetime.now(tz=timezone.utc)


class BasicApplication(factory.alchemy.SQLAlchemyModelFactory):  # pylint: disable=too-few-public-methods
    class Meta:  # pylint: disable=too-few-public-methods
        model = Application
        sqlalchemy_session = Session

    client_id = factory.LazyFunction(_id_generator)
    user = factory.SubFactory(BasicUser)
    user_id = factory.LazyAttribute(lambda a: a.user.id)
    grant_type = 'authorization_code'
    response_type = ''
    scopes = factory.LazyAttribute(lambda a: a.default_scopes)
    default_scopes = 'default_scope'
    redirect_uris = factory.LazyAttribute(lambda a: a.default_redirect_uri)
    default_redirect_uri = 'http://test.url/auth'


class BasicAuthorizationCode(factory.alchemy.SQLAlchemyModelFactory):  # pylint: disable=too-few-public-methods
    class Meta:  # pylint: disable=too-few-public-methods
        model = AuthorizationCode
        sqlalchemy_session = Session

    application = factory.SubFactory(BasicApplication)
    application_id = factory.LazyAttribute(lambda a: a.application.id)
    user = factory.SubFactory(BasicUser)
    user_id = factory.LazyAttribute(lambda a: a.user.id)
    expires_at = datetime.now(tz=timezone.utc) + timedelta(hours=1)


class BasicBearerToken(factory.alchemy.SQLAlchemyModelFactory):  # pylint: disable=too-few-public-methods
    class Meta:  # pylint: disable=too-few-public-methods
        model = BearerToken
        sqlalchemy_session = Session

    application = factory.SubFactory(BasicApplication)
    application_id = factory.LazyAttribute(lambda a: a.application.id)
    access_token = factory.LazyFunction(_id_generator)
    user = factory.SubFactory(BasicUser)
    user_id = factory.LazyAttribute(lambda a: a.user.id)
    refresh_token = factory.LazyFunction(_id_generator)
    expires_at = datetime.now(tz=timezone.utc) + timedelta(hours=1)


@pytest.fixture
def clear_database():
    """
    clears all the database, you should maintain that fixture as
    you add models,
    I don't think it's optimized but i've not seen other ways of doing that
    """
    def clear():
        BearerToken.query.delete()
        AuthorizationCode.query.delete()
        Application.query.delete()
        User.query.delete()

    return clear


@pytest.fixture
def model_factory():

    """
    creates the models that the tester will need
    """

    class ModelFactory(object):

        @staticmethod
        def save_application(*args, **kwargs):
            return BasicApplication.create(*args, **kwargs)  # pylint: disable=no-member

        @staticmethod
        def save_user(*args, **kwargs):
            return BasicUser.create(*args, **kwargs)  # pylint: disable=no-member

        @staticmethod
        def save_authorization_code(*args, **kwargs):
            return BasicAuthorizationCode.create(*args, **kwargs)  # pylint: disable=no-member

    return ModelFactory


class TestOAuthApp(TestApp):  # pylint: disable=too-few-public-methods,too-many-instance-attributes

    """
    webtest app extension for oauth authentication
    """

    def __init__(self, *args, **kwargs):
        super(TestOAuthApp, self).__init__(*args, **kwargs)
        self.auth_headers = {}
        self.get = self._add_auth_headers(self.get)
        self.post = self._add_auth_headers(self.post)
        self.put = self._add_auth_headers(self.put)
        self.patch = self._add_auth_headers(self.patch)
        self.delete = self._add_auth_headers(self.delete)
        self.options = self._add_auth_headers(self.options)
        self.head = self._add_auth_headers(self.head)
        self.application = None
        self.user = None
        self.token = None
        self.scopes = None

    def authenticate(self, application=None, user=None, scopes=''):
        #TODO validate the scopes and the application_id
        self.user = user or BasicUser()
        self.scopes = scopes
        self.application = application or BasicApplication(
            user=self.user, default_scopes=self.scopes)
        self.token = BasicBearerToken(application=self.application,
                                      user=self.user,
                                      scopes=self.scopes)
        self.auth_headers['Authorization'] = 'Bearer {}'.format(self.token.access_token)

    def _add_auth_headers(self, func):

        """
        decorator for the basic http methods to authenticate them
        """

        def wrapper(url, params=None, headers=None, *args, **kwargs):
            if headers is None:
                headers = {}
            headers.update(self.auth_headers)
            if params is not None and headers != {}:
                return func(url, params, headers, *args, **kwargs)
            if headers != {}:
                return func(url, headers=headers, *args, **kwargs)
            if params is not None:
                return func(url, params=params, *args, **kwargs)
            return func(url, *args, **kwargs)

        return wrapper


@pytest.fixture
def webtest_app():
    return TestOAuthApp(api)
