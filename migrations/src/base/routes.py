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

from flask import render_template, redirect, request, url_for  # noqa : pylint: disable=import-error
from flask_login import current_user, login_required, login_user, logout_user  # noqa : pylint: disable=import-error

from base import blueprint
from base import db, login_manager
import migrations


@blueprint.route('/')
def route_default():
  print("hi")
  print("hi")
  print("hi")
  try:
    migrations.migrations()
    return render_template('success' + '.html')
  except Exception as e:
    print("Error")
    print(e)
    return render_template('fail' + '.html')
