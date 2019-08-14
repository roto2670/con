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
import json
import logging

from flask import render_template, request, redirect  # noqa : pylint: disable=import-error
from flask_login import current_user  # noqa : pylint: disable=import-error

import util
from dashboard import count
from dashboard import blueprint


SCHEDULE_COMMON_FILE_NAME = '''schedule'''
LOCATION_MAP_COMMON_FILE_NAME = '''location.png'''
LOCATION_MAP_URI = "/dashboard/static/location/{org_id}/{file_name}"


@blueprint.route('/testcheck/bus', methods=['GET'])
@util.require_login
def default_test_bus():
  return json.dumps(count.test())


@blueprint.route('/testcheck', methods=['GET'])
@util.require_login
def default_test():
  return json.dumps(count.test_count())


@blueprint.route('/', methods=['GET'])
@util.require_login
def default_route():
  emergency_cache = count.get_emergency_info()
  return render_template("dashboard_home.html",
                         emergency=emergency_cache[count.IS_EMERGENCY_KEY],
                         time_msg=emergency_cache[count.TIME_MSG_KEY],
                         date_msg=emergency_cache[count.DATE_MSG_KEY])


@blueprint.route('/emergency', methods=['POST'])
@util.require_login
def default_emergency():
  cur_time = request.form.get('cur_time')
  cur_date = request.form.get('cur_date')
  is_emergency = json.loads(request.form.get('emergency'))
  return count.set_emergency(is_emergency, cur_time, cur_date)


@blueprint.route('/count', methods=['GET'])
@util.require_login
def default_count():
  return count.default_count()


@blueprint.route('/count/detail', methods=['GET'])
@util.require_login
def detail_count():
  return count.detail_count()


@blueprint.route('/count/reset', methods=['GET'])
@util.require_login
def reset_count():
  return count.clear_all()


@blueprint.route('/workschedule', methods=['GET'])
@util.require_login
def default_workschedule():
  base_path = util.get_static_path()
  org_path = os.path.join(base_path, 'dashboard', 'workschedule',
                          current_user.organization_id)
  file_path = os.path.join(org_path, SCHEDULE_COMMON_FILE_NAME)
  if os.path.exists(file_path):
    path = '/static/dashboard/workschedule/' + current_user.organization_id + \
         "/" + SCHEDULE_COMMON_FILE_NAME
  else:
    path = ""
  return render_template("workschedule.html", img_src=path)


@blueprint.route('/workschedule/detail', methods=['GET'])
@util.require_login
def default_workschedule_detail():
  base_path = util.get_static_path()
  org_path = os.path.join(base_path, 'dashboard', 'workschedule_d',
                          current_user.organization_id)
  file_path = os.path.join(org_path, SCHEDULE_COMMON_FILE_NAME)
  if os.path.exists(file_path):
    path = '/static/dashboard/workschedule_d/' + current_user.organization_id + \
         "/" + SCHEDULE_COMMON_FILE_NAME
  else:
    path = ""
  return render_template("workschedule_detail.html", img_src=path)


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


@blueprint.route('/workschedule/detail/view', methods=['GET'])
@util.require_login
def get_workschedule_detail():
  base_path = util.get_static_path()
  org_path = os.path.join(base_path, 'dashboard', 'workschedule_d',
                          current_user.organization_id)
  file_path = os.path.join(org_path, SCHEDULE_COMMON_FILE_NAME)
  if os.path.exists(file_path):
    return '/static/dashboard/workschedule_d/' + current_user.organization_id + \
         "/" + SCHEDULE_COMMON_FILE_NAME
  else:
    return ""


@blueprint.route('/count/settings/facescanner', methods=['GET'])
@util.require_login
def default_facescanner_setting_page():
  return count.facescanner_list()


@blueprint.route('/count/settings/beaconscanner', methods=['GET'])
@util.require_login
def default_count_setting_page():
  return count.device_list()


@blueprint.route('/count/settings/<device_id>', methods=['POST'])
@util.require_login
def default_count_setting(device_id):
  return count.set_device(device_id)


@blueprint.route('/device/refresh', methods=['GET'])
@util.require_login
def default_refresh_device():
  org_id = current_user.organization_id
  # TODO: Refresh beacon list to apiserver?
  return redirect("/dashboard/count/settings")


@blueprint.route('/bus/settings', methods=['POST'])
@util.require_login
def set_bus_settting():
  # bus_user_id from facestation, bus_beacon_id from mib
  bus_user_id = request.form.get('bus_user_id')
  bus_user_name = request.form.get('bus_user_name')
  bus_beacon_id = request.form.get('bus_beacon_id')
  return count.set_bus_setting(bus_user_id, bus_user_name, bus_beacon_id)


@blueprint.route('/bus/delete/<_id>/beacon/<bus_beacon_id>', methods=['GET'])
@util.require_login
def delete_bus_settting(_id, bus_beacon_id):
  return count.delete_bus_setting(_id, bus_beacon_id)


@blueprint.route('/count/settings/delete/<device_id>/typ/<typ>', methods=['GET'])
@util.require_login
def default_count_delete(device_id, typ):
  return count.delete_device(device_id, int(typ))


@blueprint.route('/count/settings/equip/kind/<equip_key>', methods=['POST'])
@util.require_login
def default_equip_operator_count_setting(equip_key):
  value = request.form.get('equip_worker_count')
  return count.set_equip_operator_count(equip_key, value)


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


@blueprint.route('/count/equip/counting/<key>', methods=['GET'])
@util.require_login
def get_equip_count(key):
  equip_count = count.get_equip_count(int(key))
  return json.dumps(equip_count)


@blueprint.route('/count/equip/counting/total', methods=['GET'])
@util.require_login
def get_total_equip_count():
  total_equip_count = count.get_total_equip()
  return json.dumps(total_equip_count)


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
  return redirect("/dashboard/workschedule")


@blueprint.route('/workschedule/detail/upload', methods=['POST'])
@util.require_login
def upload_workschedule_detail():
  upload_file = request.files['file']
  content = upload_file.read()
  base_path = util.get_static_path()
  org_path = os.path.join(base_path, 'dashboard', 'workschedule_d',
                          current_user.organization_id)
  if not os.path.exists(org_path):
    os.makedirs(org_path)
  file_path = os.path.join(org_path, SCHEDULE_COMMON_FILE_NAME)
  if os.path.exists(file_path):
    os.remove(file_path)
  with open(file_path, 'wb') as f:
    f.write(content)
  os.chmod(file_path, stat.S_IREAD)
  return redirect("/dashboard/workschedule/detail")


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


@blueprint.route('/worker_logs', methods=["GET"])
@util.require_login
def get_enterence_worker_log():
  return render_template("worker_logs.html")


@blueprint.route('/equip_logs', methods=["GET"])
@util.require_login
def get_enterence_equip_log():
  return render_template("equip_logs.html")
