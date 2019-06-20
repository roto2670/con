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

from flask import request
from flask_login import current_user

import apis
import util
import dash_apis
import base.routes
import dashboard
from dash import blueprint
import in_config_apis
from util import RedisStore

REDIS_HOST = '127.0.0.1'
REDIS_PORT = 6379
BEACONS_REDIS_DB = 1
WORKER_REDIS_DB = 2


# DETECTED_BEACONS = RedisStore(REDIS_HOST, REDIS_PORT, BEACONS_REDIS_DB)
DETECTED_BEACONS = {}
WORKER_COUNT = RedisStore(REDIS_HOST, REDIS_PORT, WORKER_REDIS_DB)
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
        "product_id": "mibsskec",
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
  # TODO: Not config data.... is not get scanner list
  if not config_data:
    return json.dumps([])
  ret = dash_apis.get_scanner_list(config_data.kind)
  new_ret = []
  for scanner in ret:
    if scanner['kind'] == "com.thenaran.rtos.m":
      new_ret.append(scanner)
  return json.dumps(new_ret)


@blueprint.route('/beacons/detected/<hub_id>', methods=["GET"])
@util.require_login
def get_detected_beacons_by_hub(hub_id):
  """
  :param : hub_id
  :return : dist info (dict(max = 30))
  :content : hub_id를 기준으로 주변의 비콘을 스캔한 정보를 가져온다.
  """
  ret = dash_apis.get_detected_beacons(hub_id)
  set_total_equip(current_user.organization_id, hub_id, ret['data'])
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


@blueprint.route('/cam/list/<product_id>', methods=["GET"])
@util.require_login
def get_cam_list(product_id):
  ret = dash_apis.get_cam_list(product_id)
  return json.dumps(ret)


@blueprint.route('/hubs/update', methods=["POST"])
@util.require_login
def update_scanner():
  """
  :param : None
  :return : bool
  :content : body에 custom정보가 담긴 hub data 를 post 한다
  """
  json_data = request.get_json()
  hub_data = json_data['hub']
  ret = dash_apis.update_scanner(hub_data)
  return json.dumps(ret)


@blueprint.route('/cam/location', methods=["POST"])
@util.require_login
def update_cam_location():
  json_data = request.get_json()
  cam_data = json_data['cam']
  ret = dash_apis.update_cam_location(cam_data)
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


def set_total_equip(org_id, hid, dist_data_list):
  device_data = in_config_apis.get_device_data(hid, org_id)
  custom = json.loads(device_data.custom)
  if "is_counted_hub" and 'map_location' in custom:
    if custom['is_counted_hub']:
      gid_set = set([dist_data['gid'] for dist_data in dist_data_list])
      if org_id in DETECTED_BEACONS:
        DETECTED_BEACONS[org_id][hid] = list(gid_set)
      else:
        DETECTED_BEACONS[org_id] = {}
        DETECTED_BEACONS[org_id][hid] = list(gid_set)
      set_equip_log(org_id, hid, dist_data_list)
    else:
      if org_id in DETECTED_BEACONS and hid in DETECTED_BEACONS[org_id]:
        DETECTED_BEACONS[org_id][hid] = []
      logging.warning("this scanner can not set count about detected data")
  else:
    DETECTED_BEACONS[org_id][hid] = []
    logging.warning("The scanner does not have custom data, Please add the "
                    "scanner to the map first. ")


EQUIP_DETECTED_TEXT = "{} has detected {}"


def set_equip_log(org_id, hid, dist_data_list):
  hub_data = in_config_apis.get_device_data(hid, org_id)
  for dist_data in dist_data_list:
    gadget_data = in_config_apis.get_device_data(dist_data['gid'], org_id)
    text = EQUIP_DETECTED_TEXT.format(hub_data.name, gadget_data.name)
    data_exist = in_config_apis.get_detected_equip_log_data(hid, dist_data['gid'],
                                                            dist_data['_t'])
    if not data_exist:
      in_config_apis.create_detected_equip_log(dist_data['_t'], hid, hub_data.name,
                                               dist_data['gid'], gadget_data.name,
                                               text, org_id)
    else:
      logging.warning("equip detected log is already exist")


@blueprint.route('/worker_log', methods=["GET"])
@util.require_login
def get_enterence_worker_log():
  org_id = current_user.organization_id
  _page_num = request.args.get('page_num')
  _limit = request.args.get('limit', 30)
  log_list = in_config_apis.get_enterence_worker_log_list(org_id,
                                                          page_num=int(_page_num),
                                                          limit=int(_limit))
  new_list = []
  for log in log_list.items:
    trans_dict = log.__dict__
    if '_sa_instance_state' in trans_dict:
      del trans_dict['_sa_instance_state']
    trans_dict['event_time'] = str(trans_dict['event_time'])
    trans_dict['created_time'] = str(trans_dict['created_time'])
    new_list.append(trans_dict)
  return json.dumps(new_list)


@blueprint.route('/equip_log', methods=["GET"])
@util.require_login
def get_detected_equip_log():
  org_id = current_user.organization_id
  _page_num = request.args.get('page_num')
  _limit = request.args.get('limit', 30)
  log_list = in_config_apis.get_detected_equip_log_list(org_id,
                                                        page_num=int(_page_num),
                                                        limit=int(_limit))
  new_list = []
  for log in log_list.items:
    trans_dict = log.__dict__
    if '_sa_instance_state' in trans_dict:
      del trans_dict['_sa_instance_state']
    trans_dict['event_time'] = str(trans_dict['event_time'])
    trans_dict['created_time'] = str(trans_dict['created_time'])
    new_list.append(trans_dict)
  return json.dumps(new_list)
