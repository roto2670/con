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
import os
import logging
import logging.handlers
from datetime import timedelta
from importlib import import_module


from flask import Flask  # noqa : pylint: disable=import-error
from flask import session
from flask_cors import CORS

import apis
import common
import base.routes
import dashboard.count
import back_scheduler
from base import db, auth, login_manager
from config import DebugConfig, ProductionConfig

sys.dont_write_bytecode = True


def register_extensions(app):
  db.init_app(app)
  db.app = app
  auth.init_app(app)
  login_manager.init_app(app)
  # custom
  app.context_processor(base.routes.about_product)
  app.context_processor(common.get_message)
  # jinja
  app.jinja_env.filters['datetimeFilter'] = base.routes.datetime_filter
  app.jinja_env.filters['timestampFilter'] = base.routes.timestamp_filter
  app.jinja_env.filters['getCountryName'] = base.routes.get_country_name
  app.jinja_env.filters['getLogId'] = base.routes.get_log_id


def register_blueprints(app):
  blueprints = [
      'base',
      'home',
      'products',
      'endpoints',
      'release',
      'dashboard',
      'management',
      'dash',
      'openapi',
      'maintenance',
      'registration',
      'moi',
      'login'
  ]
  for blueprint in blueprints:
    module = import_module('{}.routes'.format(blueprint))
    app.register_blueprint(module.blueprint)


def configure_database(app):
  @app.teardown_request
  def shutdown_session(exception=None):
    db.session.remove()

  db.create_all()


def configure_login(app):
  @app.before_request
  def before_request():
    session.permanent = True
    app.permanent_session_lifetime = timedelta(minutes=30)


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
  if apis.IS_DEV:
    app.config.from_object(DebugConfig)
  else:
    app.config.from_object(ProductionConfig)
  apis.init(app)
  configure_logs(app)
  register_extensions(app)
  register_blueprints(app)
  configure_database(app)
  dashboard.count.init()
  configure_login(app)
  back_scheduler.init()
  common.start()
  return app


if not apis.IS_DEV:
  # gunicorn
  __app = create_app()
  __app.debug = False


if  __name__ == '__main__':
  _app = create_app()
  if apis.IS_DEV:
    _app.debug = True
    CORS(_app)
    _app.run(host='127.0.0.1', port=5000, use_reloader=False)
  else:
    cur_path = os.path.dirname(os.path.abspath(__file__))
    ssl_path = os.path.join(cur_path, 'ssl')
    ssl_crt = os.path.join(ssl_path, 'mib_io.crt')
    ssl_key = os.path.join(ssl_path, 'mib_io.key')
    _app.debug = False
    _app.run(host='127.0.0.1', port=5000, ssl_context=(ssl_crt, ssl_key))
