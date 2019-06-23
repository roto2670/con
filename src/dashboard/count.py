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


import time
import logging

from flask import abort, render_template, request, redirect, url_for  # noqa : pylint: disable=import-error
from flask_login import current_user  # noqa : pylint: disable=import-error

import in_config_apis
from util import RedisStore
from third import suprema_apis
from config_models import FACE_STATION_TYPE


REDIS_HOST = '127.0.0.1'
REDIS_PORT = 6379
BEACONS_REDIS_DB = 1
WORKER_REDIS_DB = 2
EXPIRE_REDIS_DB = 3

# DETECTED_BEACONS = RedisStore(REDIS_HOST, REDIS_PORT, BEACONS_REDIS_DB)
WORKER_COUNT = RedisStore(REDIS_HOST, REDIS_PORT, WORKER_REDIS_DB)
EXPIRE_CACHE = RedisStore(REDIS_HOST, REDIS_PORT, EXPIRE_REDIS_DB)
EQUIPMENT_EVENT = 1
WORKER_EVENT = 2

EXPIRE_TIME = 15

IN_SETTING_ID = 1
OUT_SETTING_ID = 2

IN_OUT_SETTING_ID = {
  IN_SETTING_ID: "In",
  OUT_SETTING_ID: "Out",
  0: "None"
}

IN_LIST = set([])  # [device_id, ..]
OUT_LIST = set([])   # [device_id, ..]

ACCESS_1_ID = 1
ACCESS_2_ID = 2

ACCESS_POINT = {
  ACCESS_1_ID: "AT 1",
  ACCESS_2_ID: "AT 2",
  0: "None"
}
REVERSE_ACCESS_POINT = {
  ACCESS_1_ID: ACCESS_2_ID,
  ACCESS_2_ID: ACCESS_1_ID
}

DEVICE_LIST = {}   # {org_id : [list]}
DEVICE_LIST_TIME = {}  # {org_id : time}
INTERVAL_TIME = 600  # 10m

CHECKING_DEVICE_LIST = set([])  # [device_id, ..]
AT_1_DEVICE_LIST = set([])
AT_2_DEVICE_LIST = set([])


def default_count():
  _org_id = current_user.organization_id
  worker_interval = 10
  equip_interval = 10
  suprema_config = in_config_apis.get_suprema_config_by_org(_org_id)
  location_config = in_config_apis.get_location_config_by_org(_org_id)
  if suprema_config:
    worker_interval = suprema_config.client_interval
  if location_config:
    equip_interval = location_config.client_interval
  return render_template("dashboard_count.html", worker_interval=worker_interval,
                         equip_interval=equip_interval, device_list=device_list)


def _get_device_list(config, org_id):
  resp = suprema_apis.get_device_list(config)
  device_list = resp['DeviceCollection']['rows']
  DEVICE_LIST[org_id] = device_list
  DEVICE_LIST_TIME[org_id] = time.time()
  return device_list


def device_list():
  _org_id = current_user.organization_id
  device_list = []
  setting_id_list = []
  settings_dict = {}
  settings = in_config_apis.get_count_device_setting(FACE_STATION_TYPE)
  for setting in settings:
    setting_id_list.append(setting.device_id)
    settings_dict[setting.device_id] = setting
  suprema_config = in_config_apis.get_suprema_config_by_org(_org_id)
  if suprema_config:
    if _org_id in DEVICE_LIST_TIME:
      if (time.time() - DEVICE_LIST_TIME[_org_id]) >= INTERVAL_TIME:
        device_list = _get_device_list(suprema_config, _org_id)
      else:
        device_list = DEVICE_LIST[_org_id]
    else:
      device_list = _get_device_list(suprema_config, _org_id)
  return render_template("count_settings.html", device_list=device_list,
                         in_out_setting=IN_OUT_SETTING_ID,
                         access_point=ACCESS_POINT,
                         setting_id_list=setting_id_list,
                         settings_dict=settings_dict)


def __set_inout(inout, device_id):
  if inout == IN_SETTING_ID:
    IN_LIST.add(device_id)
  elif inout == OUT_SETTING_ID:
    OUT_LIST.add(device_id)
  else:
    if device_id in IN_LIST:
      IN_LIST.remove(device_id)
    else:
      OUT_LIST.remove(device_id)


def __set_access_point(ap, device_id):
  if ap == ACCESS_1_ID:
    CHECKING_DEVICE_LIST.add(device_id)
    AT_1_DEVICE_LIST.add(device_id)
  elif ap == ACCESS_2_ID:
    CHECKING_DEVICE_LIST.add(device_id)
    AT_2_DEVICE_LIST.add(device_id)
  else:
    if device_id in AT_1_DEVICE_LIST:
      AT_1_DEVICE_LIST.remove(device_id)
      if not AT_1_DEVICE_LIST:
        clear_keys(ACCESS_1_ID)
    else:
      AT_2_DEVICE_LIST.remove(device_id)
      if not AT_2_DEVICE_LIST:
        clear_keys(ACCESS_2_ID)


def set_device(device_id):
  inout = int(request.form.get('inout', 0))
  ap = int(request.form.get('ap'))
  typ = int(request.form.get('typ'))
  in_config_apis.create_or_update_count_device_setting(device_id, typ, inout, ap)
  __set_inout(inout, device_id)
  __set_access_point(ap, device_id)
  return redirect("/dashboard/count/settings")


def _delete_device_of_facestation(device_id):
  if device_id in CHECKING_DEVICE_LIST:
    CHECKING_DEVICE_LIST.remove(device_id)
  if device_id in AT_1_DEVICE_LIST:
    AT_1_DEVICE_LIST.remove(device_id)
  if device_id in AT_2_DEVICE_LIST:
    AT_2_DEVICE_LIST.remove(device_id)
  if device_id in IN_LIST:
    IN_LIST.remove(device_id)
  if device_id in OUT_LIST:
    OUT_LIST.remove(device_id)


def delete_device(device_id, typ):
  in_config_apis.delete_count_device_setting(device_id)
  if typ == FACE_STATION_TYPE:
    _delete_device_of_facestation(device_id)
  return redirect("/dashboard/count/settings")


def clear_keys(key):
  keys = WORKER_COUNT.hkeys(key)
  _org_id = current_user.organization_id
  WORKER_COUNT.hdel(key, *keys)
  WORKER_COUNT.hdel(_org_id, *keys)


def clear_all():
  WORKER_COUNT.flushdb()
  return redirect("/dashboard/count/settings")


WORKER_ENTER_TEXT = "{} entered {}"
WORKER_EXIT_TEXT = "{} came out {}"
WORKER_EXIT_TEXT_2 = "{} came out {}. But it entered {}"


def _set_expire_cache(user_id, user_name):
  EXPIRE_CACHE.set(user_id, user_name, EXPIRE_TIME)


def _set_worker_count(device_id, key, user_id, user_name, event_data, org_id):
  if WORKER_COUNT.has_data(org_id, user_id):
    # User exit
    if device_id in OUT_LIST:
      if WORKER_COUNT.has_data(key, user_id):
        ret = WORKER_COUNT.delete_data(key, user_id)
        ret = WORKER_COUNT.delete_data(org_id, user_id)
        text = WORKER_EXIT_TEXT.format(user_name, ACCESS_POINT[key])
        in_config_apis.create_enterence_worker_log(event_data, text, org_id)
        _set_expire_cache(user_id, user_name)
      elif WORKER_COUNT.has_data(REVERSE_ACCESS_POINT[key], user_id):
        reverse_key = REVERSE_ACCESS_POINT[key]
        ret = WORKER_COUNT.delete_data(reverse_key, user_id)
        ret = WORKER_COUNT.delete_data(org_id, user_id)
        text = WORKER_EXIT_TEXT_2.format(user_name, ACCESS_POINT[key],
                                        ACCESS_POINT[reverse_key])
        in_config_apis.create_enterence_worker_log(event_data, text, org_id)
        _set_expire_cache(user_id, user_name)
    else:
      logging.debug("%s device_id is IN type device. user name : %s",
                    device_id, user_name)
  else:
    # User enter
    if device_id in IN_LIST:
      ret = WORKER_COUNT.set_data(key, user_id, user_name)
      ret = WORKER_COUNT.set_data(org_id, user_id, user_name)
      text = WORKER_ENTER_TEXT.format(user_name, ACCESS_POINT[key])
      in_config_apis.create_enterence_worker_log(event_data, text, org_id)
      _set_expire_cache(user_id, user_name)
    else:
      logging.debug("%s device_id is OUT type device. user name : %s",
                    device_id, user_name)


def set_worker_count(org_id, user_id, name, event_data):
  device_id = event_data['device_id']['id']
  if device_id in CHECKING_DEVICE_LIST and not EXPIRE_CACHE.exists(user_id):
    if device_id in AT_1_DEVICE_LIST:
      _set_worker_count(device_id, ACCESS_1_ID, user_id, name, event_data,
                        org_id)
    elif device_id in AT_2_DEVICE_LIST:
      _set_worker_count(device_id, ACCESS_2_ID, user_id, name, event_data,
                        org_id)
  else:
    has_checking = device_id in CHECKING_DEVICE_LIST
    has_expire = EXPIRE_CACHE.exists(user_id)
    logging.debug("Checking Device : %s, Expire Cache : %s, Device : %s, name : %s",
                  has_checking, has_expire, device_id, name)


def get_total_worker():
  at1_count = WORKER_COUNT.get_data_size(ACCESS_1_ID)
  at2_count = WORKER_COUNT.get_data_size(ACCESS_2_ID)
  return at1_count + at2_count


def get_worker_count(key):
  worker_count = WORKER_COUNT.get_data_size(key)
  return worker_count


def _set_access_point(access_point, device_id):
  if access_point == ACCESS_1_ID:
    CHECKING_DEVICE_LIST.add(device_id)
    AT_1_DEVICE_LIST.add(device_id)
  elif access_point == ACCESS_2_ID:
    CHECKING_DEVICE_LIST.add(device_id)
    AT_2_DEVICE_LIST.add(device_id)


def _set_in_out_setting(inout, device_id):
  if inout == IN_SETTING_ID:
    IN_LIST.add(device_id)
  elif inout == OUT_SETTING_ID:
    OUT_LIST.add(device_id)


def init():
  org_id = '''ac983bfaa401d89475a45952e0a642cf'''
  settings = in_config_apis.get_count_device_setting(FACE_STATION_TYPE, org_id)
  for setting in settings:
    device_id = setting.device_id
    access_point = setting.access_point
    inout = setting.inout
    _set_access_point(access_point, device_id)
    _set_in_out_setting(inout, device_id)
