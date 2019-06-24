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
from config_models import SCANNER_TYPE


REDIS_HOST = '127.0.0.1'
REDIS_PORT = 6379
BEACONS_REDIS_DB = 1
WORKER_REDIS_DB = 2
EXPIRE_REDIS_DB = 3

# AT1 : 1 , AT2: 2
BEACONS_COUNT = RedisStore(REDIS_HOST, REDIS_PORT, BEACONS_REDIS_DB)
# AT1 + AT2 : org_id, AT1 : 1, AT2: 2, AT1_OP : 3, AT2_OP : 4
WORKER_COUNT = RedisStore(REDIS_HOST, REDIS_PORT, WORKER_REDIS_DB)
EXPIRE_CACHE = RedisStore(REDIS_HOST, REDIS_PORT, EXPIRE_REDIS_DB)

EXPIRE_TIME = 15
EQUIP_EXPIRE_TIME = 300
EQUIP_OPERATOR_COUNT_KEY = '''equip-operator'''
DEVICE_DATA_KEY = '''device-data'''

IN_SETTING_ID = 1
OUT_SETTING_ID = 2

IN_OUT_SETTING_ID = {
  IN_SETTING_ID: "In",
  OUT_SETTING_ID: "Out",
  0: "None"
}

ACCESS_1_ID = 1
ACCESS_2_ID = 2

# Using operator count
ACCESS_1_OPERATOR_ID = 3
ACCESS_2_OPERATOR_ID = 4

ACCESS_POINT = {
  ACCESS_1_ID: "AT 1",
  ACCESS_2_ID: "AT 2",
  0: "None"
}
REVERSE_ACCESS_POINT = {
  ACCESS_1_ID: ACCESS_2_ID,
  ACCESS_2_ID: ACCESS_1_ID
}
OPERATOR_COUNT_KEY = {
  ACCESS_1_ID: ACCESS_1_OPERATOR_ID,
  ACCESS_2_ID: ACCESS_2_OPERATOR_ID
}

# {{{ Worker count(facestation)

IN_LIST = set([])  # [device_id, ..]
OUT_LIST = set([])   # [device_id, ..]

CHECKING_DEVICE_LIST = set([])  # [device_id, ..]
AT_1_DEVICE_LIST = set([])
AT_2_DEVICE_LIST = set([])

# FaceSTation
DEVICE_LIST = {}   # {org_id : [list]}  # FaceStation Device List
DEVICE_LIST_TIME = {}  # {org_id : time}  # FaceStation Device refresh time
INTERVAL_TIME = 600  # 10m


GADGET_INFO = {
    "1": "JUMBO DRILL(2B)",
    "2": "JUMBO DRILL(3B)",
    "3": "CHARGING CAR",
    "4": "WHEEL LOADER",
    "5": "DUMP TRUCK",
    "6": "EXCAVATOR(WHEEL)",
    "7": "EXCAVATOR(CRAWLER)",
    "8": "SHOTCRETE MACHINE",
    "9": "JCB",
    "10": "CORE DRILLING MACHINE",
    "11": "DOZER",
    "12": "GROUTING MACHINE",
    "13": "MAI PUMP",
    "14": "MOBILE PRODUCTION UNIT",
    "15": "CHARGING PUMP UNIT",
    "16": "BUS"
}


# }}}

# {{{ Equip

S_CHECKING_DEVICE_LIST = set([])  # [device_id, ..]
S_AT_1_DEVICE_LIST = set([])
S_AT_2_DEVICE_LIST = set([])

# }}}


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
  device_list = []  # facestation
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
  equip_kind_settings = get_equip_operator_count_settings()
  scanners = in_config_apis.get_count_device_setting(SCANNER_TYPE)
  for scanner in scanners:
    setting_id_list.append(scanner.device_id)
    settings_dict[scanner.device_id] = scanner
  return render_template("count_settings.html", device_list=device_list,
                         in_out_setting=IN_OUT_SETTING_ID,
                         access_point=ACCESS_POINT,
                         setting_id_list=setting_id_list,
                         settings_dict=settings_dict,
                         scanner_list=scanners,
                         equip_kind_list=GADGET_INFO,
                         equip_kind_settings=equip_kind_settings)


def __fs_set_inout(inout, device_id):
  if inout == IN_SETTING_ID:
    IN_LIST.add(device_id)
  elif inout == OUT_SETTING_ID:
    OUT_LIST.add(device_id)
  else:
    if device_id in IN_LIST:
      IN_LIST.remove(device_id)
    else:
      OUT_LIST.remove(device_id)


def __fs_set_access_point(ap, device_id):
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


def __sc_set_access_point(ap, device_id):
  if ap == ACCESS_1_ID:
    S_CHECKING_DEVICE_LIST.add(device_id)
    S_AT_1_DEVICE_LIST.add(device_id)
  elif ap == ACCESS_2_ID:
    S_CHECKING_DEVICE_LIST.add(device_id)
    S_AT_2_DEVICE_LIST.add(device_id)
  else:
    if device_id in AT_1_DEVICE_LIST:
      S_AT_1_DEVICE_LIST.remove(device_id)
      if not S_AT_1_DEVICE_LIST:
        clear_keys_of_sc(ACCESS_1_ID)
    else:
      S_AT_2_DEVICE_LIST.remove(device_id)
      if not AT_2_DEVICE_LIST:
        clear_keys_of_sc(ACCESS_2_ID)


def set_device(device_id):
  inout = int(request.form.get('inout', 0))
  ap = int(request.form.get('ap'))
  typ = int(request.form.get('typ'))
  in_config_apis.create_or_update_count_device_setting(device_id, typ, inout, ap)
  if typ == FACE_STATION_TYPE:
    __fs_set_inout(inout, device_id)
    __fs_set_access_point(ap, device_id)
  elif typ == SCANNER_TYPE:
    __sc_set_access_point(ap, device_id)
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


def _delete_device_of_scanner(device_id):
  if device_id in S_CHECKING_DEVICE_LIST:
    S_CHECKING_DEVICE_LIST.remove(device_id)
  if device_id in S_AT_1_DEVICE_LIST:
    S_AT_1_DEVICE_LIST.remove(device_id)
  if device_id in S_AT_2_DEVICE_LIST:
    S_AT_2_DEVICE_LIST.remove(device_id)


def delete_device(device_id, typ):
  if typ == FACE_STATION_TYPE:
    in_config_apis.delete_count_device_setting(device_id)
    _delete_device_of_facestation(device_id)
  elif typ == SCANNER_TYPE:
    in_config_apis.reset_count_device_setting(device_id)
    _delete_device_of_scanner(device_id)
  return redirect("/dashboard/count/settings")


def clear_keys(key):
  keys = WORKER_COUNT.hkeys(key)
  _org_id = current_user.organization_id
  WORKER_COUNT.hdel(key, *keys)
  WORKER_COUNT.hdel(_org_id, *keys)


def clear_all():
  WORKER_COUNT.flushdb()
  return redirect("/dashboard/count/settings")


def clear_keys_of_sc(key):
  keys = BEACONS_COUNT.hkeys(key)
  _org_id = current_user.organization_id
  BEACONS_COUNT.hdel(key, *keys)
  BEACONS_COUNT.hdel(_org_id, *keys)


def clear_all_of_sc():
  BEACONS_COUNT.flushdb()
  return redirect("/dashboard/count/settings")


WORKER_ENTER_TEXT = "{} entered {}"
WORKER_EXIT_TEXT = "{} came out {}"
WORKER_EXIT_TEXT_2 = "{} came out {}. But it entered {}"


def _set_expire_cache(user_id, user_name):
  EXPIRE_CACHE.set(user_id, user_name, EXPIRE_TIME)


def _set_expire_equip_cache(gid, value):
  EXPIRE_CACHE.set(gid, value, EQUIP_EXPIRE_TIME)


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
  at1_op_count = WORKER_COUNT.get_data_size(ACCESS_1_OPERATOR_ID)
  at2_op_count = WORKER_COUNT.get_data_size(ACCESS_2_OPERATOR_ID)
  return at1_count + at2_count + at1_op_count + at2_op_count


def get_worker_count(key):
  worker_count = WORKER_COUNT.get_data_size(key)
  operator_count = WORKER_COUNT.get_data_size(OPERATOR_COUNT_KEY[key])
  return worker_count + operator_count


def _get_tags(tags):
  if tags:
    return tags[0]
  return None


def _check_equip_operator_count(tags):
  # tags must be size 1. value is gadget(equip) kind. ex) tags : ['1'], ['4']
  tag = _get_tags(tags)
  if tag:
    return True if BEACONS_COUNT.has_data(EQUIP_OPERATOR_COUNT_KEY, tag) else False
  return False


def _handle_operator_count(operator_key, gid, name):
  if WORKER_COUNT.has_data(operator_key, gid):
    WORKER_COUNT.delete_data(operator_key, gid)
  else:
    WORKER_COUNT.set_data(operator_key, gid, name)


EQUIP_ENTER_TEXT = "{} entered {}"
EQUIP_EXIT_TEXT = "{} came out {}"
EQUIP_EXIT_TEXT_2 = "{} came out {}. But it entered {}"


def _set_equip_count(key, org_id, gid, hid):
  device_info = get_device_data_info(gid)
  device_name = device_info.get('name', '')
  device_tag = _get_tags(device_info['tags'])
  if not device_tag:
    device_tag = 100  # None
  scanner_info = get_device_data_info(hid)
  scanner_name = scanner_info.get('name', '')
  has_count_operator = _check_equip_operator_count(device_info['tags'])
  if BEACONS_COUNT.has_data(org_id, gid):
    # equip exit
    if BEACONS_COUNT.has_data(key, gid):
      ret = BEACONS_COUNT.delete_data(key, gid)
      ret = BEACONS_COUNT.delete_data(org_id, gid)
      # Equip operator count
      if has_count_operator:
        operator_key = OPERATOR_COUNT_KEY[key]
        _handle_operator_count(operator_key, gid, device_name)
      text = EQUIP_EXIT_TEXT.format(device_name, ACCESS_POINT[key])
      in_config_apis.create_entrance_equip_log(IN_SETTING_ID, key, device_tag,
                                               hid, scanner_name, gid,
                                               device_name, text, org_id)
      _set_expire_equip_cache(gid, device_name)
    elif BEACONS_COUNT.has_data(REVERSE_ACCESS_POINT[key], gid):
      reverse_key = REVERSE_ACCESS_POINT[key]
      ret = BEACONS_COUNT.delete_data(reverse_key, gid)
      ret = BEACONS_COUNT.delete_data(org_id, gid)
      # Equip operator count
      if has_count_operator:
        operator_key = OPERATOR_COUNT_KEY[reverse_key]
        _handle_operator_count(operator_key, gid, device_name)
      text = EQUIP_EXIT_TEXT_2.format(device_name, ACCESS_POINT[key],
                                      ACCESS_POINT[reverse_key])
      in_config_apis.create_entrance_equip_log(IN_SETTING_ID, key, device_tag,
                                               hid, scanner_name, gid,
                                               device_name, text, org_id)
      _set_expire_equip_cache(gid, device_name)
  else:
    # equip enter
    ret = BEACONS_COUNT.set_data(key, gid, device_name)
    ret = BEACONS_COUNT.set_data(org_id, gid, device_name)
    # Equip operator count
    if has_count_operator:
      operator_key = OPERATOR_COUNT_KEY[key]
      _handle_operator_count(operator_key, gid, device_name)
    text = EQUIP_ENTER_TEXT.format(device_name, ACCESS_POINT[key])
    in_config_apis.create_entrance_equip_log(IN_SETTING_ID, key, device_tag,
                                             hid, scanner_name, gid, device_name,
                                             text, org_id)
    _set_expire_equip_cache(gid, device_name)


def set_equip_count(org_id, hid, dist_data_list):
  if hid in S_CHECKING_DEVICE_LIST:
    gid_set = set([dist_data['gid'] for dist_data in dist_data_list])
    for gid in gid_set:
      if not EXPIRE_CACHE.exists(gid) and hid in S_AT_1_DEVICE_LIST:
        _set_equip_count(ACCESS_1_ID, org_id, gid, hid)
      elif not EXPIRE_CACHE.exists(gid) and hid in S_AT_2_DEVICE_LIST:
        _set_equip_count(ACCESS_2_ID, org_id, gid, hid)


def get_total_equip():
  at1_count = BEACONS_COUNT.get_data_size(ACCESS_1_ID)
  at2_count = BEACONS_COUNT.get_data_size(ACCESS_2_ID)
  return at1_count + at2_count


def get_equip_count(key):
  equip_count = BEACONS_COUNT.get_data_size(key)
  return equip_count


def set_equip_operator_count(key, value):
  # key -> GADGET_INFO of key,, value = 1 or 0 -> 1 is count up/down
  if value == "0":
    if BEACONS_COUNT.has_data(EQUIP_OPERATOR_COUNT_KEY, key):
      BEACONS_COUNT.delete_data(EQUIP_OPERATOR_COUNT_KEY, key)
  else:
    BEACONS_COUNT.set_data(EQUIP_OPERATOR_COUNT_KEY, key, value)
  return redirect("/dashboard/count/settings")


def get_equip_operator_count_settings():
  equip_kind = BEACONS_COUNT.get_all(EQUIP_OPERATOR_COUNT_KEY)
  return equip_kind


def set_device_data_info(key, value):
  # key -> gid, hid,, value -> dict of data
  BEACONS_COUNT.set_data(DEVICE_DATA_KEY, key, value)


def get_device_data_info(key):
  return BEACONS_COUNT.get_data(DEVICE_DATA_KEY, key)


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


def _set_access_point_of_sc(access_point, device_id):
  if access_point == ACCESS_1_ID:
    S_CHECKING_DEVICE_LIST.add(device_id)
    S_AT_1_DEVICE_LIST.add(device_id)
  elif access_point == ACCESS_2_ID:
    S_CHECKING_DEVICE_LIST.add(device_id)
    S_AT_2_DEVICE_LIST.add(device_id)


def init():
  org_id = '''ac983bfaa401d89475a45952e0a642cf'''
  settings = in_config_apis.get_count_device_setting(FACE_STATION_TYPE, org_id)
  for setting in settings:
    device_id = setting.device_id
    access_point = setting.access_point
    inout = setting.inout
    _set_access_point(access_point, device_id)
    _set_in_out_setting(inout, device_id)

  s_settings = in_config_apis.get_count_device_setting(SCANNER_TYPE, org_id)
  for setting in s_settings:
    device_id = setting.device_id
    access_point = setting.access_point
    _set_access_point_of_sc(access_point, device_id)