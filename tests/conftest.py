import os
import tempfile

import pytest
from portfolio import create_app
from portfolio.db import get_db, init_db

with open(os.path.join(os.path.dirname(__file__), 'data.sql'), 'rb') as f:
    _data_sql = f.read().decode('utf8')

# Pytest uses fixtures by matching their function names with the names of arguments in the test functions.
@pytest.fixture
def app():
    # Creates and opens a temporary file, returning the file object and the path to it.
    db_fd, db_path = tempfile.mkstemp()

    # The app fixture will call the factory and pass test_config to configure the application
    # and database for testing instead of using your local development configuration.
    app = create_app({
        # Tells Flask that the app is in test mode.
        'TESTIING': True,
        # The DATABASE path is overridden so it points to this temporary path instead of the instance folder. 
        'DATABASE': db_path,
    })

    with app.app_context():
        init_db()
        get_db().executescript(_data_sql)

    yield app

    os.close(db_fd)
    os.unlink(db_path)

# Tests will use the client to make requests to the application without running the server.
@pytest.fixture
def client(app):
    return app.test_client()

# Creates a runner that can call the Click commands registered with the application.
@pytest.fixture
def runner(app):
    return app.test_cli_runner()

class AuthActions(object):
    def __init__(self, client):
        self._client = client

    def login(self, username='test', password='test'):
        return self._client.post(
            '/auth/login',
            data = {'username' : username,
                    'password' : password}
        )
    
    def logout(self):
        return self._client.get('/auth/logout')


# With the auth fixture, you can call auth.login() in a test to log in as the test user, which was inserted as part of the test data in the app fixture.
@pytest.fixture
def auth(client):
    return AuthActions(client)
