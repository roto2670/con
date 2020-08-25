# -*- coding: utf-8 -*-
#
# Copyright 2017-2019 Naran Inc. All rights reserved.
#  __    _ _______ ______   _______ __    _
# |  |  | |   _   |    _ | |   _   |  |  | |
# |   |_| |  |_|  |   | || |  |_|  |   |_| |
# |       |       |   |_||_|       |       |
# |  _    |       |    __  |       |  _    |
# | | |   |   _   |   |  | |   _   | | |   |
# |_|  |__|__| |__|___|  |_|__| |__|_|  |__|


import json
import logging

from flask import render_template, redirect, request  # noqa : pylint: disable=import-error
from flask_login import current_user  # noqa : pylint: disable=import-error

import base
import util
import models
import in_apis
from covid19 import blueprint


@blueprint.route('/')
@util.require_login
def route_default():
  return render_template("dashboard.html")


@blueprint.route('/users')
@util.require_login
def route_users():
  return render_template("users.html")


@blueprint.route('/notifications')
@util.require_login
def route_notifications():
  return render_template("notifications.html")


@blueprint.route('/managedata')
@util.require_login
def route_manage_data():
  return render_template("manage_data.html")