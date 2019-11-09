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
import json
import logging

from flask import abort, render_template, request, redirect, url_for  # noqa : pylint: disable=import-error
from flask_login import current_user  # noqa : pylint: disable=import-error
from flask_socketio import emit

import constants
import local_apis
import in_config_apis
from util import RedisStore
from constants import KIND_IPCAM, KIND_SPEAKER
from config_models import FACE_STATION_TYPE
from config_models import SCANNER_TYPE


REDIS_HOST = '127.0.0.1'
REDIS_PORT = 6379
BEACONS_REDIS_DB = 1
WORKER_REDIS_DB = 2
EXPIRE_REDIS_DB = 3
DATA_INFO_EXPIRE_REDIS_DB = 4
STREAMING_REDIS_DB = 5  # Using API Server
GADGET_COUNT_LIST_EXPIRE_REDIS_DB = 6


# AT1 : 1 , AT2: 2
BEACONS_COUNT = RedisStore(REDIS_HOST, REDIS_PORT, BEACONS_REDIS_DB)
# AT1 + AT2 : org_id, AT1 : 1, AT2: 2, AT1_OP : 3, AT2_OP : 4
WORKER_COUNT = RedisStore(REDIS_HOST, REDIS_PORT, WORKER_REDIS_DB)
EXPIRE_CACHE = RedisStore(REDIS_HOST, REDIS_PORT, EXPIRE_REDIS_DB)
DATA_INFO_EXPIRE_CACHE = RedisStore(REDIS_HOST, REDIS_PORT,
                                    DATA_INFO_EXPIRE_REDIS_DB)
GADGET_COUNT_LIST_EXPIRE_CACHE = RedisStore(REDIS_HOST, REDIS_PORT,
                                            GADGET_COUNT_LIST_EXPIRE_REDIS_DB)


EXPIRE_TIME = 3  # 3s
EQUIP_EXPIRE_TIME = 120  # 2m
DATA_INFO_EXPIRE_TIME = 600  # 10m
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
BUS_WORKSHOP_ID = 3
BUS_ACCESS_1_ID = 4
BUS_ACCESS_2_ID = 5

BUS_USER_GROUP_ID = '''1013'''

NORMAL_CHECK = 0
ALREADY_CHECK = 1

# Using operator count
ACCESS_1_OPERATOR_ID = 3
ACCESS_2_OPERATOR_ID = 4

ACCESS_POINT = {
  ACCESS_1_ID: "AT 1",
  ACCESS_2_ID: "AT 2",
  BUS_WORKSHOP_ID: "BUS WORKSHOP",
  BUS_ACCESS_1_ID: "BUS AT 1",
  BUS_ACCESS_2_ID: "BUS AT 2",
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

# user_id == bus_id
BUS_CHECKING_LIST = {}  # {device_id: user_id, ..}  # in checking start, not in checking end
BUS_WORKSHOP_DEVICE_LIST = set([])  # [device_id, ..]
BUS_AT_1_DEVICE_LIST = set([])
BUS_AT_2_DEVICE_LIST = set([])

# Bus setting
BUS_SETTING_DATA = {}  # {beacon_id: user_id(facestation, bus), ..}

# FaceSTation
DEVICE_LIST = {}   # {org_id : [list]}  # FaceStation Device List
DEVICE_LIST_TIME = {}  # {org_id : time}  # FaceStation Device refresh time
INTERVAL_TIME = 600  # 10m


def test():
  a = {}
  a['BUS_CHECKING_LIST'] = BUS_CHECKING_LIST
  a['BUS_WORKSHOP_DEVICE_LIST'] = list(BUS_WORKSHOP_DEVICE_LIST)
  a['BUS_AT_1_DEVICE_LIST'] = list(BUS_AT_1_DEVICE_LIST)
  a['BUS_AT_2_DEVICE_LIST'] = list(BUS_AT_2_DEVICE_LIST)
  a['BUS_SETTING_DATA'] = BUS_SETTING_DATA
  return a


def test_count():
  a = {}
  a['IN_LiST'] = list(IN_LIST)
  a['OUT_LiST'] = list(OUT_LIST)
  a['CHECKING_DEVICE_LIST'] = list(CHECKING_DEVICE_LIST)
  a['AT_1_DEVICE_LIST'] = list(AT_1_DEVICE_LIST)
  a['AT_2_DEVICE_LIST'] = list(AT_2_DEVICE_LIST)
  return a


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
    "16": "BUS",
    "17": "WCBH Drilling Machine",
    "18": "Explosive Van",
    "19": "Concrete Mixer Truck"
}
SHOT_GADGET_INFO = {
    "1": "JD-2B",
    "2": "JD-3B",
    "3": "CHARGING CAR",
    "4": "WHEEL LOADER",
    "5": "DUMP TRUCK",
    "6": "EXCAVATOR(WHEEL)",
    "7": "EXCAVATOR(CRAWLER)",
    "8": "SHOTCRETE",
    "9": "JCB",
    "10": "CORE DRILLING",
    "11": "DOZER",
    "12": "GROUTING",
    "13": "MAI PUMP",
    "14": "MPU",
    "15": "CPU",
    "16": "BUS",
    "17": "WCBH Drilling",
    "18": "Explosive Van",
    "19": "Concrete Mixer"
}

SCANNER_LOCATION = {
    "0": "PORTAL",
    "1": "AT1",
    "2": "AT2"
}


# }}}

# {{{ Equip

S_CHECKING_DEVICE_LIST = set([])  # [device_id, ..]
S_AT_1_DEVICE_LIST = set([])
S_AT_2_DEVICE_LIST = set([])

# }}}


# {{{ emergency

IS_EMERGENCY_KEY = '''is_emergency'''
TIME_MSG_KEY = '''time_msg'''
DATE_MSG_KEY = '''date_msg'''
USER_KEY = '''user'''

EMERGENCY = {
   IS_EMERGENCY_KEY: False,
   TIME_MSG_KEY: "",
   DATE_MSG_KEY: "",
   USER_KEY: ""
}

# }}}


def set_emergency(is_emergency, time_msg, date_msg):
  if is_emergency:
    EMERGENCY[IS_EMERGENCY_KEY] = is_emergency
    EMERGENCY[TIME_MSG_KEY] = time_msg
    EMERGENCY[DATE_MSG_KEY] = date_msg
    EMERGENCY[USER_KEY] = current_user.email
  else:
    EMERGENCY[IS_EMERGENCY_KEY] = is_emergency
    EMERGENCY[TIME_MSG_KEY] = ""
    EMERGENCY[DATE_MSG_KEY] = ""
    EMERGENCY[USER_KEY] = current_user.email
  return redirect("/dashboard/count")


def get_emergency_info():
  return EMERGENCY


def default_count():
  return render_template("dashboard_count.html",
                         emergency=EMERGENCY[IS_EMERGENCY_KEY],
                         time_msg=EMERGENCY[TIME_MSG_KEY],
                         date_msg=EMERGENCY[DATE_MSG_KEY])


def detail_count():
  return render_template("dashboard_count_detail.html",
                         emergency=EMERGENCY[IS_EMERGENCY_KEY],
                         time_msg=EMERGENCY[TIME_MSG_KEY],
                         date_msg=EMERGENCY[DATE_MSG_KEY])


def get_worker_data_list(ap):
  return WORKER_COUNT.get_data_of_values(ap)


def get_equip_data_list(ap):
  return BEACONS_COUNT.get_data_of_values(ap)


def get_all_equips(ap):
  return BEACONS_COUNT.get_all(ap)


def get_all_gadget_count_equips():
  # Gadget count list. Expired 20s.
  return GADGET_COUNT_LIST_EXPIRE_CACHE.get_values()


def _get_device_list(org_id):
  resp = local_apis.get_suprema_device_list()
  device_list = resp['DeviceCollection']['rows']
  DEVICE_LIST[org_id] = device_list
  DEVICE_LIST_TIME[org_id] = time.time()
  return device_list


def __add_bus_setting(bus_beacon_id, bus_user_id):
  BUS_SETTING_DATA[bus_beacon_id] = bus_user_id


def __delete_bus_setting(bus_beacon_id):
  if bus_beacon_id in BUS_SETTING_DATA:
    del BUS_SETTING_DATA[bus_beacon_id]


def set_bus_setting(bus_user_id, bus_user_name, bus_beacon_id):
  org_id = current_user.organization_id
  beacon_data = get_device_data_info(bus_beacon_id)
  in_config_apis.create_or_update_bus_setting_data(bus_user_id, bus_user_name,
                                                   bus_beacon_id, beacon_data.name,
                                                   org_id)
  __add_bus_setting(bus_beacon_id, bus_user_id)
  return redirect("/dashboard/count/settings/beaconscanner")


def delete_bus_setting(_id, bus_beacon_id):
  in_config_apis.delete_bus_setting_data(_id, current_user.organization_id)
  __delete_bus_setting(bus_beacon_id)
  return redirect("/dashboard/count/settings/beaconscanner")


def facescanner_list():
  _org_id = current_user.organization_id
  device_list = []  # facestation
  setting_id_list = []
  settings_dict = {}
  settings = in_config_apis.get_count_device_setting(FACE_STATION_TYPE)
  for setting in settings:
    setting_id_list.append(setting.device_id)
    settings_dict[setting.device_id] = setting
  if _org_id in DEVICE_LIST_TIME:
    if (time.time() - DEVICE_LIST_TIME[_org_id]) >= INTERVAL_TIME:
      device_list = _get_device_list(_org_id)
    else:
      device_list = DEVICE_LIST[_org_id]
  else:
    device_list = _get_device_list(_org_id)
  return render_template("face_settings.html", device_list=device_list,
                         in_out_setting=IN_OUT_SETTING_ID,
                         access_point=ACCESS_POINT,
                         setting_id_list=setting_id_list,
                         settings_dict=settings_dict)


def device_list():
  _org_id = current_user.organization_id
  setting_id_list = []
  settings_dict = {}
  equip_kind_settings = get_equip_operator_count_settings()
  scanners = in_config_apis.get_count_device_setting(SCANNER_TYPE, constants.ORG_ID)
  for scanner in scanners:
    setting_id_list.append(scanner.device_id)
    settings_dict[scanner.device_id] = scanner
  bus_list = get_device_data_info_list_by_tag("16")  # 16 is BUS
  bus_setting_list = in_config_apis.get_bus_setting_data_list()
  return render_template("count_settings.html",
                         in_out_setting=IN_OUT_SETTING_ID,
                         access_point=ACCESS_POINT,
                         setting_id_list=setting_id_list,
                         settings_dict=settings_dict,
                         scanner_list=scanners,
                         equip_kind_list=GADGET_INFO,
                         equip_kind_settings=equip_kind_settings,
                         bus_list=bus_list,
                         bus_setting_list=bus_setting_list)


def scanner_list():
  raw_datas = BEACONS_COUNT.get_all(DEVICE_DATA_KEY)
  data_list = []
  for raw_data in raw_datas.values():
    if 'issuer' in raw_data and raw_data['issuer'] == 'com.thenaran.skec':
      data_list.append(raw_data)
  return data_list


def beacon_list():
  raw_datas = BEACONS_COUNT.get_all(DEVICE_DATA_KEY)
  data_list = []
  for raw_data in raw_datas.values():
    if raw_data['kind'] == 'mibsskec':
      data_list.append(raw_data)
  return data_list


def ipcam_list():
  raw_datas = BEACONS_COUNT.get_all(DEVICE_DATA_KEY)
  data_list = []
  for raw_data in raw_datas.values():
    if raw_data['kind'] == KIND_IPCAM:
      data_list.append(raw_data)
  return data_list


def pa_list():
  raw_datas = BEACONS_COUNT.get_all(DEVICE_DATA_KEY)
  data_list = []
  for raw_data in raw_datas.values():
    if raw_data['kind'] == KIND_SPEAKER:
      data_list.append(raw_data)
  return data_list


def get_beacon(gid):
  data = BEACONS_COUNT.get_data(DEVICE_DATA_KEY, gid)
  return data


def get_scanner(hid):
  data = BEACONS_COUNT.get_data(DEVICE_DATA_KEY, hid)
  return data


def get_ipcam(ipcam_id):
  data = BEACONS_COUNT.get_data(DEVICE_DATA_KEY, ipcam_id)
  return data


def get_pa(pa_id):
  data = BEACONS_COUNT.get_data(DEVICE_DATA_KEY, pa_id)
  return data


def __fs_set_inout(inout, device_id):
  if inout == IN_SETTING_ID:
    IN_LIST.add(device_id)
  elif inout == OUT_SETTING_ID:
    OUT_LIST.add(device_id)
  else:
    if device_id in IN_LIST:
      IN_LIST.remove(device_id)
    elif device_id in OUT_LIST:
      OUT_LIST.remove(device_id)


def __fs_set_access_point(ap, device_id):
  if ap == ACCESS_1_ID:
    CHECKING_DEVICE_LIST.add(device_id)
    AT_1_DEVICE_LIST.add(device_id)
  elif ap == ACCESS_2_ID:
    CHECKING_DEVICE_LIST.add(device_id)
    AT_2_DEVICE_LIST.add(device_id)
  elif ap == BUS_WORKSHOP_ID:
    CHECKING_DEVICE_LIST.add(device_id)
    BUS_WORKSHOP_DEVICE_LIST.add(device_id)
  elif ap == BUS_ACCESS_1_ID:
    CHECKING_DEVICE_LIST.add(device_id)
    BUS_AT_1_DEVICE_LIST.add(device_id)
  elif ap == BUS_ACCESS_2_ID:
    CHECKING_DEVICE_LIST.add(device_id)
    BUS_AT_2_DEVICE_LIST.add(device_id)
  else:
    if device_id in AT_1_DEVICE_LIST:
      AT_1_DEVICE_LIST.remove(device_id)
      if not AT_1_DEVICE_LIST:
        clear_keys(ACCESS_1_ID)
    elif device_id in AT_2_DEVICE_LIST:
      AT_2_DEVICE_LIST.remove(device_id)
      if not AT_2_DEVICE_LIST:
        clear_keys(ACCESS_2_ID)
    elif device_id in BUS_WORKSHOP_DEVICE_LIST:
      # TODO: clear keys?
      BUS_WORKSHOP_DEVICE_LIST.remove(device_id)
    elif device_id in BUS_AT_1_DEVICE_LIST:
      # TODO: clear keys?
      BUS_AT_1_DEVICE_LIST.remove(device_id)
    elif device_id in BUS_AT_2_DEVICE_LIST:
      # TODO: clear keys?
      BUS_AT_2_DEVICE_LIST.remove(device_id)


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
    return redirect("/dashboard/count/settings/facescanner")
  elif typ == SCANNER_TYPE:
    __sc_set_access_point(ap, device_id)
    return redirect("/dashboard/count/settings/beaconscanner")
  return redirect("/dashboard/count/settings/facescanner")


def _delete_device_of_facestation(device_id):
  if device_id in CHECKING_DEVICE_LIST:
    CHECKING_DEVICE_LIST.remove(device_id)
  if device_id in AT_1_DEVICE_LIST:
    AT_1_DEVICE_LIST.remove(device_id)
  if device_id in AT_2_DEVICE_LIST:
    AT_2_DEVICE_LIST.remove(device_id)
  if device_id in BUS_WORKSHOP_DEVICE_LIST:
    BUS_WORKSHOP_DEVICE_LIST.remove(device_id)
  if device_id in BUS_AT_1_DEVICE_LIST:
    BUS_AT_1_DEVICE_LIST.remove(device_id)
  if device_id in BUS_AT_2_DEVICE_LIST:
    BUS_AT_2_DEVICE_LIST.remove(device_id)
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
    return redirect("/dashboard/count/settings/facescanner")
  elif typ == SCANNER_TYPE:
    in_config_apis.delete_count_device_setting(device_id)
    _delete_device_of_scanner(device_id)
    return redirect("/dashboard/count/settings/beaconscanner")
  return redirect("/dashboard/count/settings/facescanner")


def clear_keys(key):
  keys = WORKER_COUNT.hkeys(key)
  _org_id = current_user.organization_id
  WORKER_COUNT.hdel(key, *keys)
  WORKER_COUNT.hdel(_org_id, *keys)


def clear_all():
  WORKER_COUNT.clear_all_data()
  BEACONS_COUNT.clear_all_data()
  EXPIRE_CACHE.clear_all_data()
  return redirect("/dashboard/count")


def clear_keys_of_sc(key):
  keys = BEACONS_COUNT.hkeys(key)
  _org_id = current_user.organization_id
  BEACONS_COUNT.hdel(key, *keys)
  BEACONS_COUNT.hdel(_org_id, *keys)
  # TODO: hdel, hkeys not


def clear_all_of_sc():
  BEACONS_COUNT.flushdb()
  return redirect("/dashboard/count/settings/facescanner")


WORKER_ENTER_TEXT = "{} entered {}"
WORKER_EXIT_TEXT = "{} came out {}"
WORKER_EXIT_TEXT_2 = "{} came out {}. But it entered {}"
WORKER_ALREADY_CHECK_IN_TEXT = "{} already check-in."
WORKER_ALREADY_CHECK_OUT_TEXT = "{} already check-out"


def _set_expire_cache(user_id, user_name):
  EXPIRE_CACHE.set(user_id, user_name, EXPIRE_TIME)


def _set_expire_equip_cache(gid, value):
  EXPIRE_CACHE.set(gid, value, EQUIP_EXPIRE_TIME)


def _send_worker_log(log):
  emit('worker', json.dumps(log), namespace="/ws/log/worker", broadcast=True)


def _set_worker_count(device_id, key, user_id, user_name, event_data, org_id):
  event_data['event_time'] = in_config_apis.get_server_time()
  if WORKER_COUNT.has_data(org_id, user_id):
    # User exit
    if device_id in OUT_LIST:
      if WORKER_COUNT.has_data(key, user_id):
        ret = WORKER_COUNT.delete_data(key, user_id)
        ret = WORKER_COUNT.delete_data(org_id, user_id)
        text = WORKER_EXIT_TEXT.format(user_name, ACCESS_POINT[key])
        log = in_config_apis.create_enterence_worker_log(OUT_SETTING_ID, key,
                                                         event_data, text,
                                                         NORMAL_CHECK, org_id)
        _set_expire_cache(user_id, user_name)
        _send_worker_log(log)
      elif WORKER_COUNT.has_data(REVERSE_ACCESS_POINT[key], user_id):
        reverse_key = REVERSE_ACCESS_POINT[key]
        ret = WORKER_COUNT.delete_data(reverse_key, user_id)
        ret = WORKER_COUNT.delete_data(org_id, user_id)
        text = WORKER_EXIT_TEXT_2.format(user_name, ACCESS_POINT[key],
                                         ACCESS_POINT[reverse_key])
        log = in_config_apis.create_enterence_worker_log(OUT_SETTING_ID, key,
                                                         event_data, text,
                                                         NORMAL_CHECK, org_id)
        _set_expire_cache(user_id, user_name)
        _send_worker_log(log)
    elif device_id in BUS_AT_1_DEVICE_LIST and device_id in BUS_CHECKING_LIST:
      bus_id = BUS_CHECKING_LIST[device_id]
      WORKER_COUNT.set_data(bus_id, user_id, event_data)
      _set_expire_cache(user_id, user_name)
      # BUS_CACHE input, and later, beacon detected then count down
    elif device_id in BUS_AT_2_DEVICE_LIST and device_id in BUS_CHECKING_LIST:
      bus_id = BUS_CHECKING_LIST[device_id]
      WORKER_COUNT.set_data(bus_id, user_id, event_data)
      _set_expire_cache(user_id, user_name)
      # BUS_CACHE input, and later, beacon detected then count down
    elif device_id in IN_LIST:
      text = WORKER_ALREADY_CHECK_IN_TEXT.format(user_name)
      log = in_config_apis.create_enterence_worker_log(IN_SETTING_ID, key,
                                                       event_data, text,
                                                       ALREADY_CHECK, org_id)
      logging.debug("%s device_id is IN type device. user name : %s",
                    device_id, user_name)
    else:
      logging.debug("%s device_id is IN type or Nont type device. user name : %s",
                    device_id, user_name)
  else:
    # User enter
    if device_id in IN_LIST:
      ret = WORKER_COUNT.set_data(key, user_id, event_data)
      ret = WORKER_COUNT.set_data(org_id, user_id, event_data)
      text = WORKER_ENTER_TEXT.format(user_name, ACCESS_POINT[key])
      log = in_config_apis.create_enterence_worker_log(IN_SETTING_ID, key, event_data,
                                                       text, NORMAL_CHECK, org_id)
      _set_expire_cache(user_id, user_name)
      _send_worker_log(log)
    elif device_id in BUS_WORKSHOP_DEVICE_LIST and device_id in BUS_CHECKING_LIST:
      # BUS_CACHE input, and later, beacon detected then count up
      bus_id = BUS_CHECKING_LIST[device_id]
      WORKER_COUNT.set_data(bus_id, user_id, event_data)
      _set_expire_cache(user_id, user_name)
    elif device_id in OUT_LIST:
      text = WORKER_ALREADY_CHECK_OUT_TEXT.format(user_name)
      log = in_config_apis.create_enterence_worker_log(OUT_SETTING_ID, key,
                                                       event_data, text,
                                                       ALREADY_CHECK, org_id)
      logging.debug("%s device_id is OUT type device. user name : %s",
                    device_id, user_name)
    else:
      logging.debug("%s device_id is OUT type or None type device. user name : %s",
                    device_id, user_name)


def set_worker_count(org_id, user_id, name, event_data):
  if not EMERGENCY[IS_EMERGENCY_KEY]:
    device_id = event_data['device_id']['id']
    device_name = event_data['device_id']['name']
    user_group_id = event_data['user_group_id']['id']
    if device_id in CHECKING_DEVICE_LIST and not EXPIRE_CACHE.exists(user_id):
      if device_id in AT_1_DEVICE_LIST:
        _set_worker_count(device_id, ACCESS_1_ID, user_id, name, event_data,
                          org_id)
      elif device_id in AT_2_DEVICE_LIST:
        _set_worker_count(device_id, ACCESS_2_ID, user_id, name, event_data,
                          org_id)
      elif device_id in BUS_WORKSHOP_DEVICE_LIST:
        if user_group_id == BUS_USER_GROUP_ID:
          _check_start_end_count(user_id, device_id, device_name)
        else:
          _set_worker_count(device_id, BUS_WORKSHOP_ID, user_id, name,
                            event_data, org_id)
      elif device_id in BUS_AT_1_DEVICE_LIST:
        if user_group_id == BUS_USER_GROUP_ID:
          _check_start_end_count(user_id, device_id, device_name)
        else:
          _set_worker_count(device_id, BUS_ACCESS_1_ID, user_id, name,
                            event_data, org_id)
      elif device_id in BUS_AT_2_DEVICE_LIST:
        if user_group_id == BUS_USER_GROUP_ID:
          _check_start_end_count(user_id, device_id, device_name)
        else:
          _set_worker_count(device_id, BUS_ACCESS_2_ID, user_id, name,
                            event_data, org_id)
    else:
      has_checking = device_id in CHECKING_DEVICE_LIST
      has_expire = EXPIRE_CACHE.exists(user_id)
      logging.debug("Checking Device : %s, Expire Cache : %s, Device : %s, name : %s",
                    has_checking, has_expire, device_id, name)


def _check_start_end_count(user_id, device_id, device_name):
  if device_id in BUS_CHECKING_LIST:
    del BUS_CHECKING_LIST[device_id]
    logging.debug("%s(%s) is count end.", device_id, device_name)
  else:
    BUS_CHECKING_LIST[device_id] = user_id
    logging.debug("%s(%s) is count start.", device_id, device_name)


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


def _handle_operator_count(operator_key, gid, name=None):
  if WORKER_COUNT.has_data(operator_key, gid):
    WORKER_COUNT.delete_data(operator_key, gid)
  else:
    WORKER_COUNT.set_data(operator_key, gid, name)


def _send_equip_log(log):
  emit('equip', json.dumps(log), namespace="/ws/log/equip", broadcast=True)


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
        _handle_operator_count(operator_key, gid)
      text = EQUIP_EXIT_TEXT.format(device_name, ACCESS_POINT[key])
      log = in_config_apis.create_entrance_equip_log(OUT_SETTING_ID, key, device_tag,
                                                     hid, scanner_name, gid,
                                                     device_name, text, org_id)
      _set_expire_equip_cache(gid, device_name)
      _send_equip_log(log)

      if gid in BUS_SETTING_DATA and device_tag == "16": # 16 is bus
        bus_id = BUS_SETTING_DATA[gid]
        bus_user_list = WORKER_COUNT.get_all(bus_id)  # {user_id: event_data, ..}
        for user_id, event_data in bus_user_list.items():
          user_name = event_data['user_id']['name']
          if WORKER_COUNT.has_data(key, user_id):
            WORKER_COUNT.delete_data(key, user_id)
            WORKER_COUNT.delete_data(org_id, user_id)
            # TODO: Change text? exit with bus?
            u_text = WORKER_EXIT_TEXT.format(user_name, ACCESS_POINT[key])
            log = in_config_apis.create_enterence_worker_log(OUT_SETTING_ID, key,
                                                             event_data, u_text,
                                                             NORMAL_CHECK, org_id)
            _set_expire_cache(user_id, user_name)
            _send_worker_log(log)
            WORKER_COUNT.hdel(bus_id, user_id)
    elif BEACONS_COUNT.has_data(REVERSE_ACCESS_POINT[key], gid):
      reverse_key = REVERSE_ACCESS_POINT[key]
      ret = BEACONS_COUNT.delete_data(reverse_key, gid)
      ret = BEACONS_COUNT.delete_data(org_id, gid)
      # Equip operator count
      if has_count_operator:
        operator_key = OPERATOR_COUNT_KEY[reverse_key]
        _handle_operator_count(operator_key, gid)
      text = EQUIP_EXIT_TEXT_2.format(device_name, ACCESS_POINT[key],
                                      ACCESS_POINT[reverse_key])
      log = in_config_apis.create_entrance_equip_log(OUT_SETTING_ID, key, device_tag,
                                                     hid, scanner_name, gid,
                                                     device_name, text, org_id)
      _set_expire_equip_cache(gid, device_name)
      _send_equip_log(log)

      if gid in BUS_SETTING_DATA and device_tag == "16": # 16 is bus
        bus_id = BUS_SETTING_DATA[gid]
        bus_user_list = WORKER_COUNT.get_all(bus_id)  # {user_id: event_data, ..}
        for user_id, event_data in bus_user_list.items():
          user_name = event_data['user_id']['name']
          if WORKER_COUNT.has_data(key, user_id):
            WORKER_COUNT.delete_data(key, user_id)
            WORKER_COUNT.delete_data(org_id, user_id)
            # TODO: Change text? exit with bus?
            u_text = WORKER_EXIT_TEXT.format(user_name, ACCESS_POINT[key])
            log = in_config_apis.create_enterence_worker_log(OUT_SETTING_ID, key,
                                                             event_data, u_text,
                                                             NORMAL_CHECK, org_id)
            _set_expire_cache(user_id, user_name)
            _send_worker_log(log)
            WORKER_COUNT.hdel(bus_id, user_id)
  else:
    # equip enter
    device_data = {
        "device_name": device_name, "tag": device_tag,
        "event_time": in_config_apis.get_servertime()
    }
    ret = BEACONS_COUNT.set_data(key, gid, device_data)
    ret = BEACONS_COUNT.set_data(org_id, gid, device_data)
    # Equip operator count
    if has_count_operator:
      operator_key = OPERATOR_COUNT_KEY[key]
      _handle_operator_count(operator_key, gid, device_data)
    text = EQUIP_ENTER_TEXT.format(device_name, ACCESS_POINT[key])
    log = in_config_apis.create_entrance_equip_log(IN_SETTING_ID, key, device_tag,
                                                   hid, scanner_name, gid, device_name,
                                                   text, org_id)
    _set_expire_equip_cache(gid, device_name)
    _send_equip_log(log)

    if gid in BUS_SETTING_DATA and device_tag == "16": # 16 is bus
      bus_id = BUS_SETTING_DATA[gid]
      bus_user_list = WORKER_COUNT.get_all(bus_id)  # {user_id: event_data, ..}
      for user_id, event_data in bus_user_list.items():
        user_name = event_data['user_id']['name']
        WORKER_COUNT.set_data(key, user_id, event_data)
        WORKER_COUNT.set_data(org_id, user_id, event_data)
        # TODO: Change text? enter with bus?
        u_text = WORKER_ENTER_TEXT.format(user_name, ACCESS_POINT[key])
        log = in_config_apis.create_enterence_worker_log(IN_SETTING_ID, key, event_data,
                                                         u_text, NORMAL_CHECK, org_id)
        WORKER_COUNT.hdel(bus_id, user_id)
        _send_worker_log(log)


def set_equip_count(org_id, hid, dist_data_list):
  if not EMERGENCY[IS_EMERGENCY_KEY]:
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
  return redirect("/dashboard/count/settings/beaconscanner")


def get_equip_operator_count_settings():
  equip_kind = BEACONS_COUNT.get_all(EQUIP_OPERATOR_COUNT_KEY)
  return equip_kind


def set_device_data_info(key, value, is_force=False):
  # key -> gid, hid,, value -> dict of data
  if DATA_INFO_EXPIRE_CACHE.exists(key) and not is_force:
    return False
  BEACONS_COUNT.set_data(DEVICE_DATA_KEY, key, value)
  DATA_INFO_EXPIRE_CACHE.set(key, value, DATA_INFO_EXPIRE_TIME)
  return True


def get_device_data_info(key):
  return BEACONS_COUNT.get_data(DEVICE_DATA_KEY, key)


def get_device_data_info_list_by_tag(tag):
  ret_list = []
  value_list = BEACONS_COUNT.get_data_of_values(DEVICE_DATA_KEY)
  for value in value_list:
    if value['tags'] and value['tags'][0] == tag:
      ret_list.append(value)
  return ret_list


def _set_access_point(access_point, device_id):
  if access_point == ACCESS_1_ID:
    CHECKING_DEVICE_LIST.add(device_id)
    AT_1_DEVICE_LIST.add(device_id)
  elif access_point == ACCESS_2_ID:
    CHECKING_DEVICE_LIST.add(device_id)
    AT_2_DEVICE_LIST.add(device_id)
  elif access_point == BUS_WORKSHOP_ID:
    CHECKING_DEVICE_LIST.add(device_id)
    BUS_WORKSHOP_DEVICE_LIST.add(device_id)
  elif access_point == BUS_ACCESS_1_ID:
    CHECKING_DEVICE_LIST.add(device_id)
    BUS_AT_1_DEVICE_LIST.add(device_id)
  elif access_point == BUS_ACCESS_2_ID:
    CHECKING_DEVICE_LIST.add(device_id)
    BUS_AT_2_DEVICE_LIST.add(device_id)


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


def _set_bus_setting(bus_beacon_id, bus_user_id):
  BUS_SETTING_DATA[bus_beacon_id] = bus_user_id


def init():
  org_id = constants.ORG_ID
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

  bus_settings = in_config_apis.get_bus_setting_data_list(org_id)
  for setting in bus_settings:
    bus_beacon_id = setting.bus_beacon_id
    bus_user_id = setting.bus_user_id
    _set_bus_setting(bus_beacon_id, bus_user_id)
