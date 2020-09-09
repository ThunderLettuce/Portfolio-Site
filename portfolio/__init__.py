import os
from flask import Flask

def create_app(test_config=None):
    # Create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, '/portfolio.sqlite'),
    )

    if test_config is None:
        # Load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # Load the test config if passes in
        app.config.from_mapping(test_config)

    # Ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # A simple page that says hello
    @app.route('/hello')
    def hello():
        return 'Hello, World'

    from . import db
    db.init_app(app)

    # The authentication blueprint will have views to register new users and to log in and log out.
    from . import auth
    app.register_blueprint(auth.bp)

    return app

    # To run app:
    # $ source flask_portfolio_venv/bin/activate
    # $ export FLASK_APP=portfolio
    # $ export FLASK_APP=development
    # $ flask run