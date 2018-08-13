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


class Config(object):
  SECRET_KEY = 'key'
  SQLALCHEMY_DATABASE_URI = 'sqlite:///database.db'
  #SQLALCHEMY_DATABASE_URI = 'mysql://root:sksmswkd1@127.0.0.1:3306/console?charset=utf8'
  SQLALCHEMY_TRACK_MODIFICATIONS = False
  FIREBASE_API_KEY = 'AIzaSyANO3vuNoPC1eQjqsIJeZzGZhl1gWAPbro'
  FIREBASE_PROJECT_ID = 'console-4196c'
  FIREBASE_AUTH_SIGN_IN_OPTIONS = 'email,google'
  LOG_PATH = '/tmp/console.log'
  LOG_BACKUP_COUNT = 10
  LOG_MAX_BYTES = 10485760


class ProductionConfig(Config):
  DEBUG = False


class DebugConfig(Config):
  DEBUG = True
