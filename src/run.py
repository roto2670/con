# -*- coding: utf-8 -*-
#
# Copyright 2017-2020 Naran Inc. All rights reserved.
#  __    _ _______ ______   _______ __    _
# |  |  | |   _   |    _ | |   _   |  |  | |
# |   |_| |  |_|  |   | || |  |_|  |   |_| |
# |       |       |   |_||_|       |       |
# |  _    |       |    __  |       |  _    |
# | | |   |   _   |   |  | |   _   | | |   |
# |_|  |__|__| |__|___|  |_|__| |__|_|  |__|


import sys
import os
import socket
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
import dash.routes
import work.routes
import dashboard.count
from base import db, login_manager, socket_io
from config import DebugConfig, ProductionConfig


sys.dont_write_bytecode = True
ADDR_CHK_IP = '''8.8.8.8'''
ADDR_CHK_PORT = 80


def register_extensions(app):
  db.init_app(app)
  db.app = app
  login_manager.init_app(app)
  # custom
  app.context_processor(base.routes.about_product)
  app.context_processor(common.get_message)
  # jinja
  app.jinja_env.filters['getCountryName'] = base.routes.get_country_name
  app.jinja_env.filters['getLogId'] = base.routes.get_log_id
  app.jinja_env.filters['datetimeCheck'] = base.routes.datetime_check
  app.jinja_env.filters['usDateFormat'] = base.routes.change_us_format
  app.jinja_env.filters['usDateFormatOnlyDate'] = base.routes.change_us_format_for_date
  app.jinja_env.filters['duringTime'] = base.routes.during_time
  app.jinja_env.filters['isDict'] = base.routes.is_dict
  app.jinja_env.filters['secondToTimeFormat'] = base.routes.second_to_time_format
  app.jinja_env.filters['convertDatetime'] = base.routes.convert_date_time_format


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
      'registration',
      'maintenance',
      'moi',
      'pa',
      'internal',
      'login',
      'covid19',
      'work',
      'mobile'
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
    app.permanent_session_lifetime = timedelta(minutes=360)


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


def set_local_address():
  try:
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect((ADDR_CHK_IP, ADDR_CHK_PORT))
    local_addr = s.getsockname()[0]
    dash.routes.set_server_addr(local_addr)
    s.close()
  except:
    logging.exception("Fail to get internal IP address. Check your network status")


def create_app():
  app = Flask(__name__, static_folder='base/static')
  if apis.IS_DEV:
    app.config.from_object(DebugConfig)
  else:
    app.config.from_object(ProductionConfig)
  CORS(app)
  apis.init(app)
  configure_logs(app)
  register_extensions(app)
  register_blueprints(app)
  configure_database(app)
  dashboard.count.init()
  configure_login(app)
  common.start()
  set_local_address()
  conf_socket(app)
  work.routes.init()
  return app


def conf_socket(app):
  socket_io.init_app(app)


if not apis.IS_DEV:
  # gunicorn
  __app = create_app()
  __app.debug = False
  socket_io.run(__app, host='0.0.0.0', port=5000)


if  __name__ == '__main__':
  _app = create_app()
  if apis.IS_DEV:
    _app.debug = True
    #_app.run(host='127.0.0.1', port=5000, use_reloader=False)
    socket_io.run(_app, host='0.0.0.0', port=5000)
  else:
    cur_path = os.path.dirname(os.path.abspath(__file__))
    ssl_path = os.path.join(cur_path, 'ssl')
    ssl_crt = os.path.join(ssl_path, 'mib_io.crt')
    ssl_key = os.path.join(ssl_path, 'mib_io.key')
    _app.debug = False
    _app.run(host='127.0.0.1', port=5000, ssl_context=(ssl_crt, ssl_key))
