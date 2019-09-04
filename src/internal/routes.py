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

import constants
import in_config_apis
import dashboard.count
from internal import blueprint
from config_models import SCANNER_TYPE


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
    total_count = at1_count + at2_count
    emit('worker', total_count, namespace="/ws/count", broadcast=True)
    emit('worker_at1', at1_count, namespace="/ws/count", broadcast=True)
    emit('worker_at2', at2_count, namespace="/ws/count", broadcast=True)
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
