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
from moi import blueprint


@blueprint.route('/')
@util.require_login
def route_default():
  if current_user.level == models.MOI:
    return render_template("moi_dashboard.html")
  else:
    return render_template("moi_user.html")


@blueprint.route('/location')
@util.require_login
def route_dashboard_location():
  return render_template("moi_location.html")


@blueprint.route('/user')
@util.require_login
def route_user_control():
  user_list = in_apis.get_user_list_by_moi(current_user.organization_id)
  return render_template("moi_user.html", user_list=user_list)
