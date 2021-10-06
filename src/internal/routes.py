# -*- coding: utf-8 -*-
#
# Copyright 2017-2021 Naran Inc. All rights reserved.
#  __    _ _______ ______   _______ __    _
# |  |  | |   _   |    _ | |   _   |  |  | |
# |   |_| |  |_|  |   | || |  |_|  |   |_| |
# |       |       |   |_||_|       |       |
# |  _    |       |    __  |       |  _    |
# | | |   |   _   |   |  | |   _   | | |   |
# |_|  |__|__| |__|___|  |_|__| |__|_|  |__|


import json
import uuid
import hashlib
import logging

from flask import render_template, redirect, request  # noqa : pylint: disable=import-error

import constants
import local_apis
import in_config_apis
import dashboard.count
from internal import blueprint
from config_models import SCANNER_TYPE
from constants import REG_HUB_ID, REG_ACCOUNT_ID, KIND_NEW_BEACON
from constants import WHITE_LIST


# BEACON_INFO = {
#     1: 'Jumbo Drill(2B)',
#     2: 'Jumbo Drill(3B)',
#     3: 'Charging Car',
#     4: 'Wheel Loader',
#     5: 'Dump Truck',
#     6: 'Excavator(Wheel)',
#     7: 'Excavator(Crawler)',
#     8: 'Shotcrete Machine',
#     9: 'JCB',
#     10: 'Core Drilling Machine',
#     11: 'Dozer',
#     12: 'Grouting Rig',
#     13: 'Mai Pump',
#     14: 'MPU(Mobile Production Unit)',
#     15: 'CPU(Charging Pump Unit)',
#     16: 'Bus',
#     17: 'WCBH Drilling Machine',
#     18: 'Explosive Van',
#     19: 'Concrete Mixer Truck',
#     20: 'Shuttle',
#     21: 'Worker'
# };
BEACON_GROUPS = {
  'JD': 1,
  'AP': 2, # TODO:?
  'CC': 3,
  'WLD': 4,
  'DT': 5,
  # '': 6, # TODO: EXC(Wheel?)
  'EXC': 7,
  'SC': 8,
  'JCB': 9,
  'CDM': 10,
  'DZ': 11,
  'GPP': 12,
  'WT': 13,
  'MPU': 14,
  'CPU': 15,
  'BUS': 16,
  'WCBH': 17,
  'EXV': 18,
  'MX': 19,
  'SHUTTLE': 20,
  'PERSON': 21 # Reservation words that are not added to the resource group.
}


def _get_tag_from_res_group(res_group):
  return BEACON_GROUPS.get(res_group.upper(), None)


@blueprint.route('/beacon/new/register', methods=["POST"])
def internal_new_beacon_register():
  # TODO: Header handle?
  raw_data = request.get_data()
  data = json.loads(raw_data.decode('utf-8'))
  try:
    device_id = data.get('deviceId')
    res_group = data.get('res_group')
    name = data.get('name')
    _uuid = data.get('uuid')
    _major = data.get('major')
    _minor = data.get('minor')

    device_id = str(device_id)
    _major = int(_major)
    _minor = int(_minor)
    tag = _get_tag_from_res_group(res_group)

    if not tag:
      logging.warning(f"## Can not find tag. res group : {res_group}")
      return json.dumps(False)

    mac_hash = hashlib.md5()
    mac_hash.update(device_id.encode('utf-8'))
    mac_addr = mac_hash.hexdigest()[:12]
    new_id = f"{_uuid}{_major}{_minor}"
    security = uuid.uuid4().hex[:24]
    logging.info(f"## Register New Beacon from external. {data}")
    value = {
      "id": new_id,
      "mac": mac_addr,
      "name": name,
      "kind": KIND_NEW_BEACON,
      "protocol": 0,
      "firmware_version": "1.0.0",
      "model_number": 0,
      "model_name": "SKEC New Beacon",
      "sdk_version": "0.1",
      "beacon": REG_ACCOUNT_ID,
      "security": security,
      "hub_id": REG_HUB_ID,
      "account_id": REG_ACCOUNT_ID,
      "status": 0,
      "locale": "US",
      "rssi": 0,
      "battery": 0,
      "progress": 0,
      "latest_version": "0.0.0",
      "is_depr": 0,
      "custom": {},
      "tags": [tag],
      "beacon_spec": {
          "uuid": _uuid,
          "major": int(_major),
          "minor": int(_minor),
          "interval": 700,
          "during_second": 0
      },
      "img_url": ""
    }
    ret = local_apis.register_new_beacon(value)
    logging.info("## Register new beacon from external resp : %s", ret)
    local_apis.update_new_beacon_info(value, WHITE_LIST)
    return json.dumps(True)
  except Exception as e:
    logging.exception(f"##Raise error while new beacon register. data : {data} {e}")
    return json.dumps(False)


@blueprint.route('/beacon/new/delete', methods=["POST"])
def internal_new_beacon_delete():
  # TODO: Header handle?
  raw_data = request.get_data()
  data = json.loads(raw_data.decode('utf-8'))
  try:
    _uuid = data.get('uuid')
    _major = data.get('major')
    _minor = data.get('minor')
    new_id = f"{_uuid}{_major}{_minor}"
    logging.info(f"## Success delete new beacon from external. data : {data}")
    local_apis.remove_new_beacon(new_id)
    return json.dumps(True)
  except:
    logging.exception(f"##Raise error while new beacon delete. data : {data}")
    return json.dumps(False)


@blueprint.route('/scanner/update', methods=["POST"])
def internal_update_scanner():
  try:
    raw_data = request.get_data()
    logging.info("Update scanner data. raw data : %s", raw_data)
    hub_data = json.loads(raw_data.decode('utf-8'))
    custom = hub_data['custom']
    if 'is_counted_hub' in custom and custom['is_counted_hub']:
      # 0, 0 is none -> default
      device_setting = in_config_apis.get_count_device(hub_data['id'])
      access_point = device_setting.access_point if device_setting else 0
      in_config_apis.create_or_update_count_device_setting(hub_data['id'],
                                                           SCANNER_TYPE,
                                                           0, access_point,
                                                           name=hub_data['name'])
    elif 'is_counted_hub' in custom and not custom['is_counted_hub']:
      # TODO: delete count setting and delete redis ...
      dashboard.count.delete_device(hub_data['id'], SCANNER_TYPE)
    return json.dumps(True)
  except:
    logging.exception("Raise error while update scanner.")
    return json.dumps(False)


@blueprint.route('/set/equip_count', methods=["POST"])
def set_equip_count():
  try:
    raw_data = request.get_data()
    data = json.loads(raw_data.decode('utf-8'))
    hid = data['hub_id']
    dist_data_list = data['value']
    dashboard.count.set_equip_count(constants.ORG_ID, hid,
                                    dist_data_list)
    at1_count = dashboard.count.get_equip_count(1)
    at2_count = dashboard.count.get_equip_count(2)
    total_count = at1_count + at2_count
    emit('equip', total_count, namespace="/ws/count", broadcast=True)
    emit('equip_at1', at1_count, namespace="/ws/count", broadcast=True)
    emit('equip_at2', at2_count, namespace="/ws/count", broadcast=True)
    return json.dumps(True)
  except:
    logging.exception("Raise error while set equip count.")
    return json.dumps(False)


from flask_socketio import emit
from base import socket_io


@blueprint.route('/set/worker_count', methods=["POST"])
def set_worker_count():
  try:
    raw_data = request.get_data()
    data = json.loads(raw_data.decode('utf-8'))
    _data_list = data['value']
    for _data in _data_list:
      dashboard.count.set_worker_count(constants.ORG_ID,
                                       _data['user_id']['user_id'],
                                       _data['user_id']['name'], _data)
    at1_count = dashboard.count.get_worker_count(1)
    at2_count = dashboard.count.get_worker_count(2)
    camp_ab_count = dashboard.count.get_worker_count(30)
    camp_c_count = dashboard.count.get_worker_count(31)
    camp_d_count = dashboard.count.get_worker_count(32)
    total_count = at1_count + at2_count
    emit('worker', total_count, namespace="/ws/count", broadcast=True)
    emit('worker_at1', at1_count, namespace="/ws/count", broadcast=True)
    emit('worker_at2', at2_count, namespace="/ws/count", broadcast=True)
    emit('camp_ab', camp_ab_count, namespace="/ws/count", broadcast=True)
    emit('camp_c', camp_c_count, namespace="/ws/count", broadcast=True)
    emit('camp_d', camp_d_count, namespace="/ws/count", broadcast=True)
    return json.dumps(True)
  except:
    logging.exception("Raise error while set worker count.")
    return json.dumps(False)


@socket_io.on('connect', namespace="/ws/count")
def connect():
  logging.info("Connect count")


@socket_io.on('disconnect', namespace="/ws/count")
def disconnect():
  logging.info("Disconnect count")


@socket_io.on('connect', namespace="/ws/log/worker")
def connect():
  logging.info("Connect worker logs")


@socket_io.on('disconnect', namespace="/ws/log/worker")
def disconnect():
  logging.info("Disconnect worker logs")
