from app import app
from flask import render_template


@app.route('/')
def main():
    data = {'fullname': 'Nazar Shcherbii', 'title': 'Main Page'}
    return render_template('main.html', **data)


@app.route('/first_work')
def first_work():
    return render_template('first_work.html')

@app.route('/second_work')
def second_work():
    return render_template('second_work.html')