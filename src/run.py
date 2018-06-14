# -*- coding: utf-8 -*-
#
# Copyright 2017-2018 Naran Inc. All rights reserved.
#  __    _ _______ ______   _______ __    _
# |  |  | |   _   |    _ | |   _   |  |  | |
# |   |_| |  |_|  |   | || |  |_|  |   |_| |
# |       |       |   |_||_|       |       |
# |  _    |       |    __  |       |  _    |
# | | |   |   _   |   |  | |   _   | | |   |
# |_|  |__|__| |__|___|  |_|__| |__|_|  |__|

import sys

import logging
import logging.handlers
from config import DebugConfig
from importlib import import_module

from flask import Flask
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy

import base.routes
from base import db, auth, login_manager

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
      'organization',
      'products',
      'settings',
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
  log_path = app.config.get('LOG_PATH')
  max_bytes = int(app.config.get('LOG_MAX_BYTES'))
  backup_count = int(app.config.get('LOG_BACKUP_COUNT'))
  formatter = logging.Formatter('%(levelname)s\t[%(asctime)s]\t'
                                '%(lineno)d\t%(module)s\t'
                                '%(funcName)s\t%(message)s')
  logging.getLogger().setLevel(level)
  handler = logging.handlers.RotatingFileHandler(log_path,
                                                 maxBytes=max_bytes,
                                                 backupCount=backup_count)
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
  _app = create_app()
  _app.run(host='127.0.0.1', port=16000)
