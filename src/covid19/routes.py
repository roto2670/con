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
import dash.routes
from covid19 import blueprint


def is_internal(request):
  req_host = request.headers['Host']
  req_host = req_host.strip().split(":")[0]
  internal_addr = dash.routes.get_internal_server_addr()

  return req_host == internal_addr


@blueprint.route('/')
@util.require_login
def route_default():
  if current_user.level in [models.SK_ADMIN, models.SK_NORMAL,
                            models.COVID19_ADMIN, models.COVID19_TEAMDOCTOR,
                            models.COVID19_MANAGER]:
    return render_template("dashboard.html", is_internal=is_internal(request))
  else:
    return redirect('/')


@blueprint.route('/dashboard')
@util.require_login
def route_covid19_dashboard():
  return render_template("covid19_dashboard.html", is_internal=is_internal(request))

@blueprint.route('/camp-dashboard')
@util.require_login
def route_camp_dashboard():
  return render_template("camp_dashboard.html", is_internal=is_internal(request))


@blueprint.route('/users')
@util.require_login
def route_users():
  return render_template("users.html", is_internal=is_internal(request))


@blueprint.route('/notifications')
@util.require_login
def route_notifications():
  return render_template("notifications.html", is_internal=is_internal(request))


@blueprint.route('/managedata')
@util.require_login
def route_manage_data():
  return render_template("manage_data.html", is_internal=is_internal(request))


@blueprint.route('/news')
@util.require_login
def route_news():
  return render_template("news.html", is_internal=is_internal(request))


@blueprint.route('/kiosks')
@util.require_login
def route_kiosks():
  return render_template("kiosks.html", is_internal=is_internal(request))


@blueprint.route('/accesslogs')
@util.require_login
def route_accesslogs():
  return render_template("access_logs.html", is_internal=is_internal(request))


@blueprint.route('/settings')
@util.require_login
def route_settings():
  return render_template("csettings.html", is_internal=is_internal(request))


@blueprint.route('/survey')
@util.require_login
def route_survey():
  return render_template("survey.html", is_internal=is_internal(request))


@blueprint.route('/rooms')
@util.require_login
def route_rooms():
  return render_template("rooms.html", is_internal=is_internal(request))
