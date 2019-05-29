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
import models
import in_apis
import dash_apis
import base.routes
from dash import blueprint
from third import suprema_apis


DETECTED_BEACONS = {}
WORKER_COUNT = {}
IDENTIFY_SUCCESS_FINGERPRINT = "4865"
IDENTIFY_SUCCESS_FACE = "4867"
EQUIPMENT_EVENT = 1
WORKER_EVENT = 2


@blueprint.route('/info', methods=["GET"])
@util.require_login
def get_inforamtion():
  """
  :param : None
  :return : infomation of dict
  """
  if apis.IS_DEV:
    data = {
        "product_id": "mibs"
    }
    return json.dumps(data)
  else:
    prd = base.routes.get_current_product(current_user.id)
    if not prd:
      data = {
          "product_id": prd.id
      }
      return json.dumps(data)
    else:
      data = {}
      prd_list = in_apis.get_product_list(current_user.organization.id)
      for prd in prd_list:
        if prd.typ == models.PRD_TYPE_BLE:
          data["product_id"] = prd.id
          base.routes.set_current_product(prd)
          break
      return json.dumps(data)


@blueprint.route('/scanner/list', methods=["GET"])
@util.require_login
def get_scanner_list():
  """
  :param : None
  :return : hubs list (list of dict)
  :content : noti_key db의 kind를 확인 하여 서버에 Request를 보내고 그에 맞는 Hublist를 가져온다
  """
  ret = dash_apis.get_scanner_list()
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
  _set_total_equip(current_user.organization.id, hub_id, ret)
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


def _set_total_equip(org_id, hid, dist_data_list):
  gid_set = set([dist_data['gid'] for dist_data in dist_data_list['data']])
  if org_id in DETECTED_BEACONS:
    DETECTED_BEACONS[org_id][hid] = list(gid_set)
  else:
    DETECTED_BEACONS[org_id] = {}
    DETECTED_BEACONS[org_id][hid] = list(gid_set)


def _set_worker_count(org_id, user_id, name):
  if org_id in WORKER_COUNT:
    if user_id in WORKER_COUNT[org_id]:
      del WORKER_COUNT[org_id][user_id]
    else:
      WORKER_COUNT[org_id][user_id] = name
  else:
    WORKER_COUNT[org_id] = {}
    WORKER_COUNT[org_id][user_id] = name


@blueprint.route('/total_equip', methods=["GET"])
@util.require_login
def get_total_equip():
  all_gids = list(set(sum(DETECTED_BEACONS[current_user.organization.id].\
                          values(), [])))
  count = len(all_gids)
  return json.dumps(count)


@blueprint.route('/total_worker', methods=["GET"])
@util.require_login
def get_total_worker():
  count = len(WORKER_COUNT[current_user.organization.id])
  return json.dumps(count)


@blueprint.route('/set_event', methods=["POST"])
@util.require_login
def set_event():
  config_data = in_apis.get_suprema_config_by_org(current_user.organization.id)
  if config_data:
    evt_log_chk = suprema_apis.get_event_logs(config_data, "1")
    if evt_log_chk and evt_log_chk['EventCollection']['rows']:
      chk_data = evt_log_chk['EventCollection']['rows'][0]
      if config_data.last_data_id:
        if int(chk_data['id']) > int(config_data.last_data_id):
          limit = int(chk_data['id']) - int(config_data.last_data_id)
          rows = _extract_rows(config_data, limit)
          for data in rows:
            if data['event_type_id']['code'] == IDENTIFY_SUCCESS_FINGERPRINT:
              user_info = data['user_id']
              _set_worker_count(config_data.organization_id, user_info['user_id'],
                                user_info['name'])
              last_id = data['id']
          in_apis.update_suprema_config_about_last_id(config_data.organization_id,
                                                      config_data.base_url,
                                                      last_id)
          return json.dumps(True)
        elif int(config_data.last_data_id) == int(chk_data['id']):
          logging.warning("Server has no more event. wait for next event")
          return json.dumps(False)
        else:
          logging.warning("Data Sync is not matched please check your log")
          return json.dumps(None)
      else:
        in_apis.update_suprema_config_about_last_id(config_data.organization_id,
                                                    config_data.base_url,
                                                    chk_data['id'])
        if chk_data['event_type_id']['code'] == IDENTIFY_SUCCESS_FINGERPRINT:
          _set_worker_count(config_data.organization_id,
                            chk_data['user_id']['user_id'],
                            chk_data['user_id']['name'])
          return json.dumps(True)
    else:
      logging.warning("No logs exist on the server.")
      return json.dumps(False)
  else:
    logging.warning("api login data is not exist please login first")
    return json.dumps(False)


def _extract_rows(config_data, data_limit):
  evt_log = suprema_apis.get_event_logs(config_data, data_limit)
  rows = evt_log['EventCollection']['rows']
  rows = sorted(rows, key=lambda k: k['id'])
  return rows


@blueprint.route('/set_api_config', methods=["POST"])
@util.require_login
def set_api_config():
  """
  :request_body:
  {
    "value":
        {
          "id": "admin"
          "pw": "adminadmin1"
          "url": "http://skbs1.prota.space/api/"
        }
  }
  """
  value = request.form['value']
  config_data = in_apis.get_suprema_config_by_org(current_user.organization.id)
  if config_data:
    logging.info("suprema api login data is already exist")
    return json.dumps(True)
  else:
    base_url = value['url']
    id = value['id']
    pw = value['pw']
  login_resp = suprema_apis.login_sup_server(id, pw, base_url)
  if login_resp:
    in_apis.create_suprema_config(base_url, id, pw,
                                  current_user.organization.id)
    return json.dumps(True)
  else:
    return json.dumps(False)


@blueprint.route('/get_api_config', methods=["GET"])
@util.require_login
def get_api_config():
  ret = {}
  config_data = in_apis.get_suprema_config_by_org(current_user.organization.id)
  ret['id'] = config_data.suprema_id
  ret['pw'] = config_data.suprema_pw
  ret['base_url'] = config_data.base_url
  return json.dumps(ret)


@blueprint.route('/update_api_config', methods=["POST"])
@util.require_login
def update_api_config():
  """
  :request_body:
  {
    "value":
        {
          "id": "admin"
          "pw": "adminadmin1"
          "url": "http://skbs1.prota.space/api/"
        }
  }
  """
  value = request.form['value']
  in_apis.update_suprema_config_about_config_data(current_user.organization.id,
                                                  value['id'],
                                                  value['pw'],
                                                  value['url'])
  return json.dumps(True)
