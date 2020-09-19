from flask import Blueprint, flash, g, redirect, render_template, request, url_for
from werkzeug.exceptions import abort
from flaskr.auth import login_required
from flaskr.db import get_db

# Creates a Blueprint named 'auth'. Like the application object, the blueprint needs to know where it’s defined, so __name__ is passed as the second argument.
# The url_prefix will be prepended to all the URLs associated with the blueprint.
bp = Blueprint('blog', __name__)

# The index will show all of the posts, most recent first.
# JOIN is used so that the author info from the user table is available in the result.


@bp.route('/')
def index():
    db = get_db()
    posts = db.execute(
        'SELECT p.id, title, body, created, author_id, username'
        ' FROM post p JOIN user u ON p.author_id = u.id'
        ' ORDER BY created DESC'
    ).fetchall()
    return render_template('blog/index.html', posts=posts)


# The create view works the same as the auth register view.
# Either the form is displayed, or the posted data is validated and the post is added to the database or an error is shown.
@bp.route('/create', methods=('GET', 'POST'))
# A user must be logged in to visit these views, otherwise they will be redirected to the login page.
@login_required
def create():
    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        error = None

        # If missing title throw error
        if not title:
            erro - 'Title is required'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'INSERT INTO post (title, body, author_id)'
                ' VALUES (?, ?, ?)',
                (title, body, g.user['id'])
            )
            bd.commit()
            return redirect(url_for('blog.index'))

    return render_template('blog/create.html')

# The check_author argument is defined so that the function can be used to get a post without checking the author.
def get_post(id, check_author=True):
    post = get_db().execute(
        'SELECT p.id, title, body, created, author_id, username'
        ' FROM post p JOIN user u ON p.author_id = u.id'
        ' WHERE p.id = ?',
        (id,)
    ).fetchone()

    if post is None:
        abort(404, f'Post id {id} doesn\'t exist.')

    if check_author and post['author_id'] != g.user['id']:
        abort(403)

    return post


# The update function takes an argument, id.
# That corresponds to the <int:id> in the route.
# A real URL will look like /1/update. Flask will capture the 1, ensure it’s an int, and pass it as the id argument. 
# To generate a URL to the update page, url_for() needs to be passed the id so it knows what to fill in: url_for('blog.update', id=post['id']).
@bp.route('/<int:id>/update', methods=('GET', 'POST'))
@login_required
def update(id):
    post = get_post(id)

    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        error = None

        if not title:
            error = 'Title is required.'

        if error is not None:
            flash(error)
        else:
            db.get_db()
            db.execute(
                'UPDATE post SET title = ?, body = ?'
                ' WHERE id = ?',
                (title, body, id)
            )
            db.commit()
            return redirect(url_for('blog.index'))

    return render_template('blog/update.html', post=post)


# The delete view doesn’t have its own template, the delete button is part of update.html and posts to the /<id>/delete URL.
# Since there is no template, it will only handle the POST method and then redirect to the index view.
@bp.route('/<int:id>/delete', methods('POST',))
@login_required
def delete(id):
    get_post(id)
    db = get_db()
    db.execute('DELETE FROM post WHERE id = ?', (id,))
    db.commit()
    return redirect(url_for('blog/index'))
