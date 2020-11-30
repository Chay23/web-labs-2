from flask import Flask
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from flask_admin.contrib.fileadmin import FileAdmin

from config import Config

app = Flask(__name__)
app.config.from_object(Config)

db = SQLAlchemy(app)
migrate = Migrate(app, db)
bcrypt = Bcrypt(app)
login = LoginManager(app)
login.login_view = 'login'
login.login_message_category = 'info'
login.session_protection = "strong"

#admin flask
from .models import User, Post
from app.forms import PostModelView, MyIndexView

admin = Admin(app, name='Blog', template_mode='bootstrap3', index_view=MyIndexView())
admin.add_view(ModelView(User, db.session))
admin.add_view(PostModelView(Post, db.session))
admin.add_view(FileAdmin(app.config['STATIC_DIR'], '/static/', name='Static Files'))

from app import views, models
