import pytest
from portfolio import g, session
from portfolio.db import get_db

def test_register(client, app):
    # Makes a GET request and returns the Response object returned by Flask.
    # Test that the page renders successfully, a simple request is made and checked for a 200 OK status_code.
    # If rendering failed, Flask would return a 500 Internal Server Error code.
    assert client.get('/auth/register').status_code == 200
    # Makes a POST request, converting the data dict into form data.
    response = client.post(
        # data contains the body of the response as bytes. 
        # If you expect a certain value to render on the page, check that it’s in data. Bytes must be compared to bytes.
        '/auth/register', data = {'username' : 'a', 'password' : 'a'}
    )
    # headers will have a Location header with the login URL when the register view redirects to the login view.
    assert 'http://localhost/auth/login' == response.headers['Location']

    with app.app_context():
        assert get_db().execute(
            "select * from user where username = 'a'"
        ).fetchone() is not None

# Tells Pytest to run the same test function with different arguments.
@pytest.mark.parametrize(('username', 'password', 'message'), (
    # Test different invalid input and error messages without writing the same code three times.
    ('', '', b'Username is required.'),
    ('a', '', b'Password is required.'),
    ('test', 'test', b'already registered'),
))
def test_register_validate_input(client, username, password, message):
    response = client.post(
        '/auth/register',
        data = {'username' : username, 'password' : password}
    )
    assert message in response.data

def test_login(client, auth):
    assert client.get('/auth/login').status_code == 200
    response = auth.login()
    assert response.headers['Location'] == 'http://localhost/'

    # Using client in a with block allows accessing context variables such as session after the response is returned. 
    # Normally, accessing session outside of a request would raise an error.
    with client:
        client.get('/')
        assert session['user_id'] == 1
        assert g.user['username'] == 'test'

@pytest.mark.parametrize(('username', 'password', 'message'), (
    ('a', 'test', b'Incorrect username.'),
    ('test', 'a', b'Incorrect password.'),
))
def test_login_validate_input(auth, username, password, message):
    response = auth.login(username, password)
    assert message in response.data

def test_logout(client, auth):
    auth.login()

    with client:
        auth.logout()
        assert 'user_id' not in session