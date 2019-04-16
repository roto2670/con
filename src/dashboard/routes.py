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


import os, stat
import logging

from flask import abort, render_template, request, redirect, url_for  # noqa : pylint: disable=import-error
from flask_login import current_user  # noqa : pylint: disable=import-error

import util
from dashboard import blueprint


SCHEDULE_COMMON_FILE_NAME = '''schedule'''


@blueprint.route('/', methods=['GET'])
@util.require_login
def default_route():
  return render_template("dashboard_home.html")


@blueprint.route('/workschedule', methods=['GET'])
@util.require_login
def default_workschedule():
  return render_template("workschedule.html")


@blueprint.route('/workschedule/view', methods=['GET'])
@util.require_login
def get_workschedule():
  base_path = util.get_static_path()
  org_path = os.path.join(base_path, 'dashboard', 'workschedule',
                          current_user.organization_id)
  file_path = os.path.join(org_path, SCHEDULE_COMMON_FILE_NAME)
  if os.path.exists(file_path):
    return '/static/dashboard/workschedule/' + current_user.organization_id + \
         "/" + SCHEDULE_COMMON_FILE_NAME
  else:
    return ""


@blueprint.route('/workschedule/upload', methods=['POST'])
@util.require_login
def upload_workschedule():
  upload_file = request.files['file']
  content = upload_file.read()
  base_path = util.get_static_path()
  org_path = os.path.join(base_path, 'dashboard', 'workschedule',
                          current_user.organization_id)
  if not os.path.exists(org_path):
    os.makedirs(org_path)
  file_path = os.path.join(org_path, SCHEDULE_COMMON_FILE_NAME)
  with open(file_path, 'wb') as f:
    f.write(content)
  os.chmod(file_path, stat.S_IREAD)
  return '/static/dashboard/workschedule/' + current_user.organization_id + \
      "/" + SCHEDULE_COMMON_FILE_NAME


@blueprint.route('/location', methods=['GET'])
@util.require_login
def default_location():
  return render_template("location.html")
