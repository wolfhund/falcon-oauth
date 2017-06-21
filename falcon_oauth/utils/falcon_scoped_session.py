import threading

from sqlalchemy.util import ScopedRegistry
from sqlalchemy.orm import scoped_session


class FalconOauthRegistry(ScopedRegistry):

    """
    A scoped registry for a thread for falcon database
    """

    def __init__(self, createfunc):
        self.createfunc = createfunc
        self.registry = threading.local()

    def __call__(self):
        try:
            return self.registry.falcon_oauth_thread_var
        except AttributeError:
            val = self.registry.falcon_oauth_thread_var = self.createfunc()
            return val

    def has(self):
        return hasattr(self.registry, "falcon_oauth_thread_var")

    def set(self, obj):
        self.registry.falcon_oauth_thread_var = obj

    def clear(self):
        try:
            del self.registry.falcon_oauth_thread_var
        except AttributeError:
            pass

class falcon_oauth_session(scoped_session):

    """
    Database session for a thread for falcon_oauth
    """

    def __init__(self, session_factory, scopefunc=None):
        self.session_factory = session_factory

        if scopefunc:
            self.registry = ScopedRegistry(session_factory, scopefunc)
        else:
            self.registry = FalconOauthRegistry(session_factory)
