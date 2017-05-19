"""
    falcon-oauth
    ============
"""
import sys

from setuptools import setup
from setuptools.command.test import test as TestCommand


class PyTest(TestCommand):
    user_options = [('pytest-args=', 'a', '')]

    def initialize_options(self):
        TestCommand.initialize_options(self)
        self.pytest_args = ['-q', '--color=yes', '--cov=src', 'tests']

    def run_tests(self):
        #import here, cause outside the eggs aren't loaded
        import pytest
        errno = pytest.main(self.pytest_args)
        sys.exit(errno)


setup(name='falcon-oauth',
    version='0.0.1',
    description='package to integrate oauth2 with falcon',
    url='https://github.com/wolfhund/falcon-oauth',
    author='Carlos Martinez, Arnaud Paran',
    author_email='paran.arnaug@gmail.com',
    license='MIT',
    packages=['src'],
    install_requires=['oauthlib', 'alembic'],
    tests_require=['pytest-cov'],
    cmdclass={'test': PyTest},
    zip_safe=False)
