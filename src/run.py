
import sys
import logging
import logging.handlers
from importlib import import_module

from flask import Flask
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from config import DebugConfig

from base import db, auth, login_manager
import base.routes

sys.dont_write_bytecode = True

def register_extensions(app):
  db.init_app(app)
  auth.init_app(app)
  login_manager.init_app(app)
  # custom
  app.context_processor(base.routes.get_product_list)


def register_blueprints(app):
  blueprints = [
      'base',
      'home',
      'profile',
      'products',
      'login'
  ]
  for blueprint in blueprints:
    module = import_module('{}.routes'.format(blueprint))
    app.register_blueprint(module.blueprint)


def configure_database(app):

    @app.before_first_request
    def initialize_database():
        db.create_all()

    @app.teardown_request
    def shutdown_session(exception=None):
        db.session.remove()


def configure_logs(app):
  level = logging.DEBUG
  formatter = logging.Formatter('%(levelname)s\t[%(asctime)s]\t'
                                '%(lineno)d\t%(module)s\t'
                                '%(funcName)s\t%(message)s')
  logging.getLogger().setLevel(level)
  handler = logging.handlers.RotatingFileHandler(app.config.get('LOG_PATH'),
                                                 maxBytes=int(app.config.get('LOG_MAX_BYTES')),
                                                 backupCount=int(app.config.get('LOG_BACKUP_COUNT')))
  handler.setFormatter(formatter)
  logging.getLogger().addHandler(handler)


def create_app():
  app = Flask(__name__, static_folder='base/static')
  app.config.from_object(DebugConfig)
  configure_logs(app)
  register_extensions(app)
  register_blueprints(app)
  configure_database(app)
  return app


if  __name__ == '__main__':
  app = create_app()
  app.run(host='127.0.0.1', port=16000)
