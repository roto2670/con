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

from flask import request
from flask_login import current_user

import apis
import util
import dash_apis
from dash import blueprint
import in_config_apis


DETECTED_BEACONS = {}
WORKER_COUNT = {}
EQUIPMENT_EVENT = 1
WORKER_EVENT = 2


@blueprint.route('/location/info', methods=["GET"])
@util.require_login
def get_location_inforamtion():
  """
  :param : None
  :return : infomation of dict
  """
  if apis.IS_DEV:
    data = {
        "product_id": "mibs",
        "interval": 60
    }
    return json.dumps(data)
  else:
    _org_id = current_user.organization_id
    config_data = in_config_apis.get_location_config_by_org(_org_id)
    if not config_data:
      data = {
          "product_id": "",
          "interval": 0
      }
      return json.dumps(data)
    else:
      data = {
          "product_id": config_data.product_id,
          "interval": config_data.client_interval
      }
      return json.dumps(data)


@blueprint.route('/scanner/list', methods=["GET"])
@util.require_login
def get_scanner_list():
  """
  :param : None
  :return : hubs list (list of dict)
  :content : noti_key db의 kind를 확인 하여 서버에 Request를 보내고 그에 맞는 Hublist를 가져온다
  """
  config_data = in_config_apis.get_location_config_by_org(current_user.organization_id)
  ret = dash_apis.get_scanner_list(config_data.kind)
  return json.dumps(ret)


@blueprint.route('/beacons/detected/<hub_id>', methods=["GET"])
@util.require_login
def get_detected_beacons_by_hub(hub_id):
  """
  :param : hub_id
  :return : dist info (dict(max = 30))
  :content : hub_id를 기준으로 주변의 비콘을 스캔한 정보를 가져온다.
  """
  ret = dash_apis.get_detected_beacons(hub_id)
  set_total_equip(current_user.organization_id, hub_id, ret)
  return json.dumps(ret)


@blueprint.route('/hubs/detected/<gadget_id>', methods=["GET"])
@util.require_login
def get_detected_hubs_by_beacon(gadget_id):
  """
  :param : gadget_id
  :return : dist info (dict(max = 30))
  :content : gadget_id 가진 가젯을 기준으로 주변의 스캐너 거리정보를 가져온다.
  """
  query_id = request.args.get("qid", None)
  ret = dash_apis.get_detected_hubs(gadget_id, query_id=query_id)
  return json.dumps(ret)


@blueprint.route('/beacons/list/<product_id>', methods=["GET"])
@util.require_login
def get_beacon_list(product_id):
  """
  :param : product_id
  :return : gadgets(beacons) list (list of dict)
  :content : product id를 kind로 갖는 모든 gadget을 가져온다
  """
  ret = dash_apis.get_beacon_list(product_id)
  return json.dumps(ret)


@blueprint.route('/hubs/location', methods=["POST"])
@util.require_login
def update_scanner_location():
  """
  :param : None
  :return : bool
  :content : body에 custom정보가 담긴 hub data 를 post 한다
  """
  json_data = request.get_json()
  hub_data = json_data['hub']
  ret = dash_apis.update_scanner_location(hub_data)
  return json.dumps(ret)


@blueprint.route('/beacons/<beacon_id>', methods=["GET"])
@util.require_login
def get_beacon_info(beacon_id):
  """
  :param : gadget_id(beacon_id)
  :return : gadget data (dict)
  :content : 입력받은 gadget_id에 맞는 gadget data를 준다
  """
  ret = dash_apis.get_beacon_info(beacon_id)
  return json.dumps(ret)


@blueprint.route('/total_equip', methods=["GET"])
@util.require_login
def get_total_equip():
  if current_user.organization_id in DETECTED_BEACONS:
    all_gids = list(set(sum(DETECTED_BEACONS[current_user.organization_id].\
                            values(), [])))
    count = len(all_gids)
    return json.dumps(count)
  return json.dumps(0)


@blueprint.route('/total_worker', methods=["GET"])
@util.require_login
def get_total_worker():
  if current_user.organization_id in WORKER_COUNT:
    count = len(WORKER_COUNT[current_user.organization_id])
    return json.dumps(count)
  return json.dumps(0)


def set_total_equip(org_id, hid, dist_data_list):
  gid_set = set([dist_data['gid'] for dist_data in dist_data_list['data']])
  if org_id in DETECTED_BEACONS:
    DETECTED_BEACONS[org_id][hid] = list(gid_set)
  else:
    DETECTED_BEACONS[org_id] = {}
    DETECTED_BEACONS[org_id][hid] = list(gid_set)


def set_worker_count(org_id, user_id, name):
  if org_id in WORKER_COUNT:
    if user_id in WORKER_COUNT[org_id]:
      del WORKER_COUNT[org_id][user_id]
    else:
      WORKER_COUNT[org_id][user_id] = name
  else:
    WORKER_COUNT[org_id] = {}
    WORKER_COUNT[org_id][user_id] = name
