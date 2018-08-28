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


import os
import apis


class Config(object):
  SECRET_KEY = 'skfksrltnf1'
  if apis.IS_DEV:
    SQLALCHEMY_DATABASE_URI = 'sqlite:///database.db'  # SQLITE
    #SQLALCHEMY_DATABASE_URI = 'mysql://root:sksmswkd1@127.0.0.1:3306/console?charset=utf8'  # LOCAL MySQL
  else:
    SQLALCHEMY_DATABASE_URI = '''mysql+pymysql://console:skfksxpzm1@localhost:3306/console'''  # Google Cloud SQL
  SQLALCHEMY_TRACK_MODIFICATIONS = False
  FIREBASE_API_KEY = 'AIzaSyANO3vuNoPC1eQjqsIJeZzGZhl1gWAPbro'
  FIREBASE_PROJECT_ID = 'console-4196c'
  FIREBASE_AUTH_SIGN_IN_OPTIONS = 'email,google'
  if apis.IS_DEV:
    LOG_PATH = '/tmp/console.log'
  else:
    LOG_PATH = os.path.join(os.path.expanduser('~'), 'log', 'console.log')
  LOG_BACKUP_COUNT = 10
  LOG_MAX_BYTES = 10485760


class ProductionConfig(Config):
  DEBUG = False


class DebugConfig(Config):
  DEBUG = True
