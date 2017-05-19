"""
    falcon-oauth
    ============
"""
import sys
import logging.config

from setuptools import setup
from setuptools.command.test import test as TestCommand


LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'default': {
            'format': '%(asctime)s - %(levelname)s - %(name)s - %(filename)s:%(lineno)d :: %(message)s',  # pylint: disable=line-too-long
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'default',
        },
    },
    'loggers': {
        'falcon_oauth': {
            'handlers': ['console'],
            'level': 'DEBUG',
        },
        'tests': {
            'handlers': ['console'],
            'level': 'DEBUG',
        },
    },
}


class PyTest(TestCommand):
    user_options = [('pytest-args=', 'a', '')]

    def initialize_options(self):
        TestCommand.initialize_options(self)
        self.pytest_args = ['-s', '-q', '--color=yes', '--cov=falcon_oauth', 'tests']

    def run_tests(self):
        #import here, cause outside the eggs aren't loaded
        logging.config.dictConfig(LOGGING)
        import pytest
        errno = pytest.main(self.pytest_args)
        sys.exit(errno)


class Pylint(TestCommand):
    user_options = [('pylint-args=', 'a', '')]

    def initialize_options(self):
        TestCommand.initialize_options(self)
        self.pylint_args = ['-f', 'colorized', '-r', 'n', 'falcon_oauth']

    def run_tests(self):
        #import here, cause outside the eggs aren't loaded
        import pylint.lint
        errno = pylint.lint.Run(self.pylint_args)
        sys.exit(errno)



setup(name='falcon-oauth',
    version='0.0.1',
    description='package to integrate oauth2 with falcon',
    url='https://github.com/wolfhund/falcon-oauth',
    author='Carlos Martinez, Arnaud Paran',
    author_email='paran.arnaug@gmail.com',
    license='GPL',
    packages=['falcon_oauth'],
    install_requires=['oauthlib', 'alembic', 'psycopg2', 'falcon', 'pytz'],
    tests_require=['pytest-cov', 'pylint', 'webtest', 'factory-boy'],
    cmdclass={'test': PyTest, 'pylint': Pylint},
    zip_safe=False)
