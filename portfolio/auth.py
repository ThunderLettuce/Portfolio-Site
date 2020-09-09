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
            'Select id FROM user WHERE username = ?', (username,)
        # fetchone() returns one row from the query.
        ).fetchone() is not None:
        error = f'User {username} is already registered'

        if error is None:
            # If validation succeeds, insert the new user data into the database.
            # generate_password_hash() is used to securely hash the password, and that hash is stored.
            # 
            db.execute(
                'INSERT INTO user (username, password) VALUES (?, ?)',
                (username, generate_password_hash(password))
            )
            # Since this query modifies data, db.commit() needs to be called afterwards to save the changes.
            db.commit()
            # After storing the user, they are redirected to the login page.
            return redirect(url_for(auth.login))
        
        # If validation fails, the error is shown to the user.
        # flash() stores messages that can be retrieved when rendering the template.
        flash(error)

    # When the user initially navigates to auth/register, or there was a validation error, an HTML page with the registration form should be shown.
    return render_template('auth/register.html')
