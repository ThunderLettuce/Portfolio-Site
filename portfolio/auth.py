import functools

from flask import Blueprint, flash, g, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash

from portfolio.db import get_db

# Creates a Blueprint named 'auth'. Like the application object, the blueprint needs to know where it’s defined, so __name__ is passed as the second argument.
# The url_prefix will be prepended to all the URLs associated with the blueprint.
bp = Blueprint('auth', __name__, url_prefix='/auth')


@bp.route('/register', methods=('GET', 'POST'))
def register():
    if request.method == 'POST':
        # Request.form is a special type of dict mapping submitted form keys and values
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        error = None

        # Validate that username is not empty
        if not username:
            error = 'Username is required.'
        # Validate that username is not empty
        elif not password:
            error = 'Password is required.'
        # Validate that username is not already registered by querying the database and checking if a result is returned.
        elif db.execute(
            'SELECT id FROM user WHERE username = ?', (username,)
            # fetchone() returns one row from the query.
        ).fetchone() is not None:
            error = f'User {username} is already registered'

        if error is None:
            # If validation succeeds, insert the new user data into the database.
            # generate_password_hash() is used to securely hash the password, and that hash is stored.
            db.execute(
                'INSERT INTO user (username, password) VALUES (?, ?)',
                (username, generate_password_hash(password))
            )
            # Since this query modifies data, db.commit() needs to be called afterwards to save the changes.
            db.commit()
            # After storing the user, they are redirected to the login page.
            return redirect(url_for('auth.login'))

        # If validation fails, the error is shown to the user.
        # flash() stores messages that can be retrieved when rendering the template.
        flash(error)

    # When the user initially navigates to auth/register, or there was a validation error, an HTML page with the registration form should be shown.
    return render_template('auth/register.html')


@bp.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        error = None
        # The user is queried first and stored in a variable for later use.
        user = db.execute(
            'SELECT * FROM user WHERE username = ?', (username,)
        ).fetchone()

        if user is None:
            error = 'Incorrect username.'
        # check_password_hash() hashes the submitted password in the same way as the stored hash and securely compares them. If they match, the password is valid.
        elif not check_password_hash(user['password'], password):
            error = 'Incorrect password.'

        # session is a dict that stores data across requests.
        if error is None:
            session.clear()
            # When validation succeeds, the user’s id is stored in a new session.
            # The data is stored in a cookie that is sent to the browser, and the browser then sends it back with subsequent requests.
            session['user_id'] = user['id']
            return redirect(url_for('index'))

        flash(error)

    return render_template('auth/login.html')

# bp.before_app_request() registers a function that runs before the view function, no matter what URL is requested


@bp.before_app_request
# checks if a user id is stored in the session and gets that user’s data from the database, storing it on g.user, which lasts for the length of the request.
def load_logged_in_user():
    user_id = session.get('user_id')

    # If there is no user id, or if the id doesn’t exist, g.user will be None.
    if user_id is None:
        g.user = None
    else:
        g.user = get_db().execute(
            'SELECT * FROM user WHERE id = ?', (user_id,)
        ).fetchone()


@bp.route('/logout')
def logout():
    # Remove the user id from the session.
    session.clear()
    return redirect(url_for('index'))

# Creating, editing, and deleting blog posts will require a user to be logged in. A decorator can be used to check this for each view it’s applied to.


def login_required(view):
    # Decorator returns a new view function that wraps the original view it’s applied to.
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        # Checks if a user is loaded and redirects to the login page otherwise.
        if g.user is None:
            return redirect(url_for('auth.lofin'))

        # If a user is loaded the original view is called and continues normally
        return view(**kwargs)

    return wrapped_view

# When using a blueprint, the name of the blueprint is prepended to the name of the function,
# so the endpoint for the login function you wrote above is 'auth.login' because you added it to the 'auth' blueprint.
