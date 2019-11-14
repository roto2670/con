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

from flask import Blueprint  # noqa : pylint: disable=import-error
from flask_login import LoginManager  # noqa : pylint: disable=import-error
from flask_sqlalchemy import SQLAlchemy  # noqa : pylint: disable=import-error
from flask_socketio import SocketIO

blueprint = Blueprint(
    'base_blueprint',
    __name__,
    url_prefix='',
    template_folder='templates',
    static_folder='static'
)

db = SQLAlchemy()
login_manager = LoginManager()
socket_io = SocketIO()
