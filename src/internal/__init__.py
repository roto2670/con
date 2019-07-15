# -*- coding: utf-8 -*-
#
# Copyright 2019-2020 Naran Inc. All rights reserved.
#  __    _ _______ ______   _______ __    _
# |  |  | |   _   |    _ | |   _   |  |  | |
# |   |_| |  |_|  |   | || |  |_|  |   |_| |
# |       |       |   |_||_|       |       |
# |  _    |       |    __  |       |  _    |
# | | |   |   _   |   |  | |   _   | | |   |
# |_|  |__|__| |__|___|  |_|__| |__|_|  |__|

from flask import Blueprint  # noqa : pylint: disable=import-error

blueprint = Blueprint(
  'internal_blueprint',
  __name__,
  url_prefix='/internal',
  template_folder='templates',
  static_folder='static'
)
