from flask import Flask
from flask_admin import Admin
from flask_admin.contrib.fileadmin import FileAdmin
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

from config import Config

db = SQLAlchemy()
migrate = Migrate()
bcrypt = Bcrypt()
login = LoginManager()
admin = Admin(name='Blog', template_mode='bootstrap3')


def create_app(config_app=Config):
    app = Flask(__name__)
    app.config.from_object(config_app)

    db.init_app(app)
    migrate.init_app(app, db)
    bcrypt.init_app(app)
    login.init_app(app)
    login.login_view = 'user_bp.login'
    login.login_message_category = 'info'
    login.session_protection = "strong"

    from .models import User, Post, Post_API
    from app.forms import PostModelView, MyIndexView, UserAdminView, ModelView

    admin.init_app(app, index_view=MyIndexView())
    admin.add_view(UserAdminView(User, db.session))
    admin.add_view(PostModelView(Post, db.session))
    admin.add_view(ModelView(Post_API, db.session))
    admin.add_view(FileAdmin(app.config['STATIC_DIR'], '/static/', name='Static Files'))

    create_blueprints(app)

    return app


def create_blueprints(app):
    from app.post import post_bp
    from app.user import user_bp
    from app.custom_admin import custom_admin_bp
    from app.api_post import api_post_bp

    app.register_blueprint(post_bp, url_prefix='/')
    app.register_blueprint(user_bp, url_prefix='/')
    app.register_blueprint(custom_admin_bp, url_prefix='/')
    app.register_blueprint(api_post_bp, url_prefix='/api/v1/')


from app import views, models
