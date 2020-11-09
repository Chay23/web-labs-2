from flask import render_template, redirect, url_for, flash

from app import app, db
from app import bcrypt
from app.forms import LoginForm, RegistrationForm
from .models import User, Post


# @app.route('/main')
# def index():
#     return render_template('index.html', name='Інженерія програмного забезпечення', title='PNU')


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
    posts = Post.query.all()
    return render_template('posts.html', posts=posts)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data

        user = User.query.filter_by(email=email).first()

        if user and bcrypt.check_password_hash(user.password_hash, password):
            flash("Sing in successfully")
            return redirect(url_for('main'))
        else:
            flash('Login or password is incorrect', 'warning')
    return render_template('login.html', form=form)


@app.route('/register', methods=['GET', 'POST'])
def register():
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
