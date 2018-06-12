from flask import Blueprint
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy

from login import FirebaseAuth

blueprint = Blueprint(
    'base_blueprint',
    __name__,
    url_prefix='',
    template_folder='templates',
    static_folder='static'
)

db = SQLAlchemy()
auth = FirebaseAuth()
login_manager = LoginManager()