from flask import Blueprint

blueprint = Blueprint(
    'products_blueprint',
    __name__,
    url_prefix='/products',
    template_folder='templates',
    static_folder='static'
)
