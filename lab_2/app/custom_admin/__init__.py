from flask import Blueprint

custom_admin_bp = Blueprint('custom_admin_bp', __name__, template_folder='templates/custom_admin',
                            static_folder='static',
                            static_url_path='assets')

from app.custom_admin import custom_admin
