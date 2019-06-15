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

from flask import Blueprint  # noqa : pylint: disable=import-error
from flask_login import LoginManager  # noqa : pylint: disable=import-error
from flask_sqlalchemy import SQLAlchemy  # noqa : pylint: disable=import-error
from flask_caching import Cache

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
cache = Cache(config={'CACHE_TYPE': 'filesystem', 'CACHE_DIR': '/tmp'})
