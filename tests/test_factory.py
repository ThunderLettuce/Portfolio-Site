from portfolio import create_app

# The only behavior that can change is passing test config.
# If config is not passed, there should be some default configuration, otherwise the configuration should be overridden.
def test_config():
    assert not create_app().testing
    assert create_app({'TESTING' : True}).testing

def test_hello(client):
    response = client.get('/hello')
    assert response.data == b'Hello, World!'