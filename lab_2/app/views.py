from flask import render_template, flash, redirect, url_for

from app import app
from app.forms import LoginForm


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


@app.route('/login', methods=['GET','POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        flash('Login for user {} {}'.format(
            form.username.data, form.password.data))
        return redirect(url_for('login'))
    return render_template('login.html', form=form)
