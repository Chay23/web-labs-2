from flask import Blueprint

api_post_bp = Blueprint('api_post_bp', __name__)

from app.api_post import api_post
