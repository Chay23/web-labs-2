import os
import secrets
from datetime import datetime

from PIL import Image
from flask import render_template, redirect, url_for, flash, request
from flask_login import current_user, login_user, logout_user, login_required
from werkzeug.urls import url_parse

from app import app, db
from app import bcrypt
from app.forms import LoginForm, RegistrationForm, UpdateAccountForm, PostCreationForm, PostEditingForm
from .models import User, Post

ROWS_PER_PAGE = 5


@app.route('/')
def main():
    data = {'fullname': 'Nazar Shcherbii', 'title': 'Main Page'}
    return render_template('main.html', **data)


@app.route('/first')
def first_work():
    return render_template('first_work.html')


@app.route('/second')
def second_work():
    return render_template('second_work.html')


@app.route('/posts')
def posts():
    q = request.args.get('q')
    page = request.args.get('page', 1, type=int)
    if q:
        posts = Post.query.filter(Post.title.contains(q) | Post.body.contains(q))
    else:
        posts = Post.query.order_by(Post.timestamp.desc())
        # print(posts.all())

    pages = posts.paginate(page=page, per_page=ROWS_PER_PAGE)
    return render_template('posts.html', posts=posts, pages=pages, q=q)


@app.route('/post/<int:id>')
def post(id):
    post = Post.query.filter_by(id=id).first()
    return render_template('post.html', post=post)


@app.route('/create_post', methods=['GET', 'POST'])
@login_required
def create_post():
    form = PostCreationForm()
    if form.validate_on_submit():
        post_title = form.post_title.data
        post_body = form.post_body.data

        post = Post(title=post_title, body=post_body, author=current_user)

        db.session.add(post)
        db.session.commit()
        flash("Post created successfully")
        return redirect(url_for('posts'))
    return render_template('create_post.html', form=form)


@app.route('/edit_post/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_post(id):
    form = PostEditingForm()
    post = Post.query.filter_by(id=id).first()
    if form.validate_on_submit():
        if current_user.username != post.author.username:
            return redirect(url_for('main'))
        post.title = form.post_title.data
        post.body = form.post_body.data
        post.update_time = datetime.utcnow()

        db.session.commit()
        flash("Post edited successfully")

    elif request.method == 'GET':
        if current_user.username != post.author.username:
            return redirect(url_for('main'))
        form.post_title.data = post.title
        form.post_body.data = post.body
    return render_template('edit_post.html', form=form, post=post)


@app.route('/delete_post/<int:id>', methods=["GET", "DELETE"])
@login_required
def delete_post(id):
    post = Post.query.filter_by(id=id).first()
    if current_user.username != post.author.username:
        return redirect(url_for('main'))

    db.session.delete(post)
    db.session.commit()
    return redirect(url_for('posts'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main'))
    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data

        user = User.query.filter_by(email=email).first()

        if user and bcrypt.check_password_hash(user.password_hash, password):
            flash("Sing in successfully", "success")
            login_user(user, remember=form.remember_me.data)
            next_page = request.args.get('next')
            if not next_page or url_parse(next_page).netloc != '':
                next_page = url_for('main')
            return redirect(next_page)
        else:
            flash('Login or password is incorrect', 'warning')
    return render_template('login.html', form=form)


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main'))
    form = RegistrationForm()
    if form.validate_on_submit():
        username = form.username.data
        email = form.email.data
        password = form.password.data

        hashed = bcrypt.generate_password_hash(password).decode('utf-8')

        user = User(username=username, email=email, password_hash=hashed)
        db.session.add(user)
        db.session.commit()
        flash("Sing up successfully")
    return render_template('register.html', form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('main'))


@app.route('/account', methods=['GET', 'POST'])
@login_required
def account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            current_user.image_file = picture_file
        current_user.username = form.username.data
        current_user.email = form.email.data
        current_user.about_me = form.about_me.data
        if form.old_password.data:
            current_user.password_hash = bcrypt.generate_password_hash(form.new_password.data).decode('utf-8')
        db.session.commit()
        flash('Your account has been updated!', 'success')
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
        form.about_me.data = current_user.about_me
    image_file = url_for('static', filename='images/thumbnails/' + current_user.image_file)
    return render_template('account.html', title='Account', image_file=image_file, form=form, user=current_user)


def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    f_name, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = f_name + random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static/images/thumbnails/', picture_fn)
    # form_picture.save(picture_path)

    output_size = (128, 128)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)

    return picture_fn


@app.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()
