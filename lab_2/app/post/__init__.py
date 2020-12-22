from flask import Blueprint

post_bp = Blueprint('post_bp', __name__, template_folder='templates/post', static_folder='static',
                    static_url_path='assets')

from app.post import post
