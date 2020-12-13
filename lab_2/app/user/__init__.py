from flask import Blueprint

user_bp = Blueprint('user_bp', __name__, template_folder='templates/user', static_folder='static/images/thumbnails',
                     static_url_path='assets')

from app.user import user
