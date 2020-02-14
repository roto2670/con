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


import os
import apis


class Config(object):
  SECRET_KEY = 'skfksrltnf1'
  if apis.IS_DEV:
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:qlalfqjsgh1!@127.0.0.1:3306/mib_console'  # LOCAL MySQL New
    SQLALCHEMY_BINDS = {
      'mib_console': 'mysql+pymysql://root:qlalfqjsgh1!@127.0.0.1:3306/mib_console',
      'smart_work': 'mysql+pymysql://root:qlalfqjsgh1!@127.0.0.1:3306/work_prog'  # TODO: change work_prog
    }
  else:
    SQLALCHEMY_DATABASE_URI = '''mysql+pymysql://console:skfksxpzm1@localhost:3306/mib_console'''  # Google Cloud SQL
    SQLALCHEMY_BINDS = {
      'mib_console': 'mysql+pymysql://root:skfksxpzm1@127.0.0.1:3306/mib_console',
      'smart_work': 'mysql+pymysql://root:skfksxpzm1@127.0.0.1:3306/work_prog'  # TODO: change work_prog
    }
  SQLALCHEMY_TRACK_MODIFICATIONS = False
  if apis.IS_DEV:
    LOG_PATH = '/tmp/console.log'
  else:
    LOG_PATH = os.path.join(os.path.expanduser('~'), 'log', 'console.log')
  LOG_BACKUP_COUNT = 20
  LOG_MAX_BYTES = 10485760
  TOKEN = 'console-admin'


class ProductionConfig(Config):
  DEBUG = False


class DebugConfig(Config):
  DEBUG = True
