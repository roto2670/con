from flask import Blueprint
from flask_login import current_user

blueprint = Blueprint(
    'products_blueprint',
    __name__,
    url_prefix='/products',
    template_folder='templates',
    static_folder='static'
)
