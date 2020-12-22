from flask_script import Manager, prompt_bool, Command

from app import db, bcrypt
from app.models import User, Post, Post_API

manager = Manager(usage="Perform database operations")


@manager.command
def createdb():
    db.create_all()


@manager.command
def drop():
    if prompt_bool("Are you sure you want to lose all your data"):
        db.drop_all()


@manager.command
def recreate():
    if prompt_bool(
            "Are you sure you want to rebuild your database"):
        db.drop_all()


@manager.command
def init_data():
    hashed = bcrypt.generate_password_hash('pass1234').decode('utf-8')
    u = User(username="User", email="example@mail.com", password_hash=hashed, admin=True)
    db.session.add(u)
    p = Post(title="Title", body="Post example", author=u)
    p_api = Post_API(title="Title", body="Post example", user_id=u.id)
    db.session.add(p)
    db.session.add(p_api)
    db.session.commit()
    print("Initialization completed")
