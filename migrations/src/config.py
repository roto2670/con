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


class Config(object):
  SECRET_KEY = 'skfksrltnf1'
  #SQLALCHEMY_DATABASE_URI = 'mysql://root:sksmswkd1@127.0.0.1:3306/mib_console?charset=utf8'  # LOCAL MySQL
  SQLALCHEMY_DATABASE_URI = 'mysql://console:skfksxpzm1@127.0.0.1:3307/mib_console?charset=utf8'  # Cloud MySQL
  SQLALCHEMY_BINDS = {
      #"old": 'mysql://root:sksmswkd1@127.0.0.1:3306/console?charset=utf8',  # Local MySql
      "old": 'mysql://console:skfksxpzm1@127.0.0.1:3307/console?charset=utf8',  # Cloud MySql
      "new": 'mysql://console:skfksxpzm1@127.0.0.1:3307/mib_console?charset=utf8'  # Cloud MySql
      #"new": 'mysql://root:sksmswkd1@127.0.0.1:3306/mib_console?charset=utf8'  # Local MySql
  }
  SQLALCHEMY_TRACK_MODIFICATIONS = False
  FIREBASE_API_KEY = 'AIzaSyANO3vuNoPC1eQjqsIJeZzGZhl1gWAPbro'
  FIREBASE_PROJECT_ID = 'console-4196c'
  FIREBASE_AUTH_SIGN_IN_OPTIONS = 'email,google'
  LOG_PATH = '/tmp/console.log'
  LOG_BACKUP_COUNT = 10
  LOG_MAX_BYTES = 10485760
  CELERY_BACKEND = 'rpc://'
  CELERY_BROKER = 'pyamqp://console:skfksrltnf1@localhost:5672/'
  TOKEN = 'token'


class ProductionConfig(Config):
  DEBUG = False


class DebugConfig(Config):
  DEBUG = True
