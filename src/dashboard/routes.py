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
import json

from flask import abort, render_template, request, redirect, url_for  # noqa : pylint: disable=import-error
from flask_login import current_user  # noqa : pylint: disable=import-error

import util
import common
import in_apis
import in_config_apis
from dashboard import count
from dashboard import blueprint
import back_scheduler
from third import suprema_apis


SCHEDULE_COMMON_FILE_NAME = '''schedule'''
LOCATION_MAP_COMMON_FILE_NAME = '''location.png'''
LOCATION_MAP_URI = "/dashboard/static/location/{org_id}/{file_name}"


@blueprint.route('/', methods=['GET'])
@util.require_login
def default_route():
  _org_id = current_user.organization_id
  worker_interval = 10
  equip_interval = 10
  suprema_config = in_config_apis.get_suprema_config_by_org(_org_id)
  location_config = in_config_apis.get_location_config_by_org(_org_id)
  if suprema_config:
    worker_interval = suprema_config.client_interval
  if location_config:
    equip_interval = location_config.client_interval
  return render_template("dashboard_home.html", worker_interval=worker_interval,
                         equip_interval=equip_interval)


@blueprint.route('/count', methods=['GET'])
@util.require_login
def default_count():
  return count.default_count()


@blueprint.route('/workschedule', methods=['GET'])
@util.require_login
def default_workschedule():
  return render_template("workschedule.html")


@blueprint.route('/count/settings', methods=['GET'])
@util.require_login
def default_count_setting_page():
  return count.device_list()


@blueprint.route('/count/settings/<device_id>', methods=['POST'])
@util.require_login
def default_count_setting(device_id):
  return count.set_device(device_id)


@blueprint.route('/count/settings/delete/<device_id>', methods=['GET'])
@util.require_login
def default_count_delete(device_id):
  return count.delete_device(device_id)


@blueprint.route('/count/worker/counting/<key>', methods=['GET'])
@util.require_login
def get_worker_count(key):
  worker_count = count.get_worker_count(int(key))
  return json.dumps(worker_count)


@blueprint.route('/count/worker/counting/total', methods=['GET'])
@util.require_login
def get_total_worker_count():
  total_worker_count = count.get_total_worker()
  return json.dumps(total_worker_count)


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
  if os.path.exists(file_path):
    os.remove(file_path)
  with open(file_path, 'wb') as f:
    f.write(content)
  os.chmod(file_path, stat.S_IREAD)
  return '/static/dashboard/workschedule/' + current_user.organization_id + \
      "/" + SCHEDULE_COMMON_FILE_NAME


@blueprint.route('/location', methods=['GET'])
@util.require_login
def default_location():
  return render_template("location.html")


@blueprint.route('/location/view', methods=['GET'])
@util.require_login
def get_location_map():
  base_path = util.get_static_path("dashboard")
  org_path = os.path.join(base_path, 'location',
                          current_user.organization_id)
  file_path = os.path.join(org_path, LOCATION_MAP_COMMON_FILE_NAME)
  if os.path.exists(file_path):
    uri = LOCATION_MAP_URI.format(org_id=current_user.organization_id,
                                  file_name=LOCATION_MAP_COMMON_FILE_NAME)
    return uri
  else:
    return ""


@blueprint.route('/location/upload', methods=['POST'])
@util.require_login
def upload_location_map():
  upload_file = request.files['file']
  content = upload_file.read()
  base_path = util.get_static_path("dashboard")
  org_path = os.path.join(base_path, 'location',
                          current_user.organization_id)
  if not os.path.exists(org_path):
    os.makedirs(org_path)
  file_path = os.path.join(org_path, LOCATION_MAP_COMMON_FILE_NAME)
  if os.path.exists(file_path):
    os.remove(file_path)
  with open(file_path, 'wb') as f:
    f.write(content)
  os.chmod(file_path, stat.S_IREAD)
  uri = LOCATION_MAP_URI.format(org_id=current_user.organization_id,
                                file_name=LOCATION_MAP_COMMON_FILE_NAME)
  return uri


@blueprint.route('/settings', methods=['GET'])
@util.require_login
def dashboard_settings():
  _org_id = current_user.organization_id
  prd_list = in_apis.get_product_list(_org_id)
  noti_key_list = in_apis.get_noti_key_list(_org_id)
  biostar_event_list = suprema_apis.get_event_list()
  suprema_config = in_config_apis.get_suprema_config_by_org(_org_id)
  location_config = in_config_apis.get_location_config_by_org(_org_id)
  return render_template("dashboard_settings.html", prd_list=prd_list,
                         noti_key_list=noti_key_list,
                         biostar_event_list=biostar_event_list,
                         suprema_config=suprema_config,
                         location_config=location_config)


@blueprint.route('/settings/location', methods=['POST'])
@util.require_login
def set_location_settings():
  _product_id = request.form['locationPrdId']
  _client_interval = int(request.form['locationClientInterval'])
  _server_interval = int(request.form['locationServerInterval'])
  _kind = request.form['locationkindName']
  _org_id = current_user.organization_id

  config_data = in_config_apis.get_location_config_by_org(_org_id)
  if config_data:
    in_config_apis.update_location_config(_product_id, _kind, _client_interval,
                                          _server_interval, _org_id)
    logging.info("Update location Config. User : %s, Pid : %s",
                 current_user.email, _product_id)
    back_scheduler.scheduler_main_equip(_org_id, _kind, _server_interval, True)
  else:
    in_config_apis.create_location_config(_product_id, _kind, _client_interval,
                                          _server_interval, _org_id)
    logging.info("Create Suprema Config. User : %s, Pid : %s",
                 current_user.email, _product_id)
    back_scheduler.scheduler_main_equip(_org_id, _kind, _server_interval)
  return redirect("/dashboard/settings")


@blueprint.route('/settings/suprema', methods=['POST'])
@util.require_login
def set_suprema_settings():
  _id = request.form['supremaId']
  _pw = request.form['supremaPassword']
  _url = request.form['supremaBaseUrl']
  _client_interval = int(request.form['supremaClientInterval'])
  _server_interval = int(request.form['supremaServerInterval'])
  _event_id = request.form['supremaEvent']
  _org_id = current_user.organization_id

  login_result = suprema_apis.login_sup_server(_id, _pw, _url, _org_id)
  if login_result:
    config_data = in_config_apis.get_suprema_config_by_org(_org_id)
    if config_data:
      in_config_apis.update_suprema_config(_url, _id, _pw, _event_id,
                                           _client_interval, _server_interval,
                                           _org_id)
      logging.info("Update Suprema Config. User : %s, base url : %s",
                   current_user.email, _url)
      back_scheduler.scheduler_main_worker(_org_id, _server_interval, True)
    else:
      in_config_apis.create_suprema_config(_url, _id, _pw, _event_id,
                                           _client_interval, _server_interval,
                                           _org_id)
      suprema_apis.set_last_id_cache(_org_id, 0)
      logging.info("Create Suprema Config. User : %s, base url : %s",
                   current_user.email, _url)
      back_scheduler.scheduler_main_worker(_org_id, _server_interval)
    return redirect("/dashboard/settings")
  else:
    logging.warning(
        "Fail to login. Check your ID, Password.  ID : %s, Password : %s",
        _id, _pw)
    title = common.get_msg("dashboard.biostar.failed_setting_title")
    msg = common.get_msg("dashboard.biostar.failed_setting_message")
    common.set_error_message(title, msg)
    return redirect("/dashboard/settings")


@blueprint.route('/worker_logs', methods=["GET"])
@util.require_login
def get_enterence_worker_log():
  return render_template("worker_logs.html")

